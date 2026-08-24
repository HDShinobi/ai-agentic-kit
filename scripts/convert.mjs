import { AGENTS, SKILLS, COMMANDS, DROP_KEYS } from "./mapping.mjs";
import fs from "node:fs";
import path from "node:path";

const SRC = ".tmp/ag-kit-src/.agents";
const OUT = "plugins";
const flags = [];

// ---- Preflight: fail loudly if mapping and source disagree (before any write) ----
const preflight = () => {
  const problems = [];
  const check = (sub, mapObj, label, isDir) => {
    const present = fs.readdirSync(path.join(SRC, sub), { withFileTypes: true })
      .filter((e) => (isDir ? e.isDirectory() : e.isFile() && e.name.endsWith(".md")))
      .map((e) => (isDir ? e.name : e.name.replace(/\.md$/, "")));
    for (const m of Object.keys(mapObj))
      if (!present.includes(m)) problems.push(`mapping ${label} "${m}" missing from source`);
    for (const p of present)
      if (!Object.keys(mapObj).includes(p) && p !== "orchestrator") // orchestrator merged into /orchestrate (Task 5)
        problems.push(`source ${label} "${p}" not in mapping`);
  };
  check("skills", SKILLS, "skill", true);
  check("agent", AGENTS, "agent", false);
  check("workflows", COMMANDS, "command", false);
  if (problems.length) { console.error("PREFLIGHT FAILED:\n" + problems.join("\n")); process.exit(1); }
  console.log("Preflight OK.");
};

// Parse frontmatter, tolerating nested block mappings (e.g. `metadata:\n  author: x`).
// A top-level key with an empty value followed by indented lines is a "block" key;
// its raw child lines are captured in `block[key]` so they can be dropped or preserved as a unit.
const splitFrontmatter = (raw) => {
  const text = raw.replace(/\r\n/g, "\n");
  if (!text.startsWith("---\n")) return { hasFm: false, body: text };
  const end = text.indexOf("\n---\n", 4);
  if (end < 0) return { hasFm: false, body: text };
  const fm = {}; const order = []; const block = {}; let cur = null;
  for (const line of text.slice(4, end).split("\n")) {
    if (line.trim() === "") continue;
    if (/^\s/.test(line)) { // indented → child of the current block key
      if (cur === null) throw new Error(`Indented frontmatter line without parent: "${line}"`);
      block[cur].push(line);
      continue;
    }
    const mm = line.match(/^([A-Za-z0-9_-]+):\s?(.*)$/);
    if (!mm) throw new Error(`Unparseable frontmatter line: "${line}"`);
    const [, k, v] = mm;
    fm[k] = v; order.push(k);
    if (v.trim() === "") { cur = k; block[k] = []; } else { cur = null; }
  }
  return { hasFm: true, fm, body: text.slice(end + 5), order, block };
};

const unquote = (v) => String(v).replace(/^["'](.*)["']$/s, "$1");
const needsQuote = (v) => /[:#]/.test(v) || /^\s|\s$/.test(v) || /^[>|&*!%@`"'\[\]{},]/.test(v);
const emit = (k, v) => {
  const r = unquote(v);
  return needsQuote(r) ? `${k}: "${r.replace(/"/g, '\\"')}"` : `${k}: ${r}`;
};
const rebuildFrontmatter = (fm, order, block) =>
  "---\n" + order.filter((k) => !DROP_KEYS.includes(k) && fm[k] !== undefined)
    .map((k) => {
      if (block[k] && block[k].length) { // preserved block key not in DROP_KEYS
        throw new Error(`Unsupported block-mapping frontmatter key "${k}" (not droppable)`);
      }
      return emit(k, fm[k]);
    }).join("\n") + "\n---\n";

const OWNER = { skills: SKILLS, agent: AGENTS, workflows: COMMANDS };
const DEST_SEG = { skills: "skills", agent: "agents", workflows: "commands" };

// Body path handling: rewrite intra-plugin refs to the correct subdir; leave cross-plugin refs
// literal (so later audits catch them); flag every ref with file:line. Applied to ALL .md content.
const rewriteBody = (body, relFile, plugin) => {
  const out = body.split("\n").map((line, i) =>
    line.replace(/\.agents\/(skills|agent|workflows)\/([a-z0-9-]+)\//g, (m, seg, name) => {
      const owner = OWNER[seg][name];
      const cls = owner === plugin ? "intra" : "cross";
      flags.push(`${relFile}:${i + 1}\t${m}\t${cls}`);
      return cls === "intra" ? `\${CLAUDE_PLUGIN_ROOT}/${DEST_SEG[seg]}/${name}/` : m;
    })
  ).join("\n");
  body.split("\n").forEach((line, i) => {
    for (const mm of line.matchAll(/\.agents\/(rules|memory|scripts)\/\S*/g))
      flags.push(`${relFile}:${i + 1}\t${mm[0]}\tpath`);
  });
  return out;
};

// Component files (SKILL.md, agent .md, command .md): rebuild frontmatter + rewrite body.
const normalizeComponent = (raw, relFile, plugin) => {
  const fmr = splitFrontmatter(raw);
  if (!fmr.hasFm) return rewriteBody(fmr.body, relFile, plugin);
  const { fm, body, order, block } = fmr;

  if (fm.when_to_use !== undefined) { // merge into description
    fm.description = `${unquote(fm.description || "")} ${unquote(fm.when_to_use)}`.trim();
    if (!order.includes("description")) order.splice(order.indexOf("when_to_use"), 0, "description");
    delete fm.when_to_use;
  }
  if (fm.tools !== undefined) // agents: drop Agent (can't spawn subagents)
    fm.tools = fm.tools.split(",").map((s) => s.trim()).filter((t) => t && t !== "Agent").join(", ");
  // NOTE: allowed-tools Agent→Task (app-builder) / Agent-strip (coordinator-mode) are manual (Tasks 6/11).

  return rebuildFrontmatter(fm, order, block) + rewriteBody(body, relFile, plugin);
};

// Reference/sibling files: copy verbatim (CRLF-normalized), preserving their own frontmatter;
// only rewrite/flag .agents/ path refs in the body.
const normalizeReference = (raw, relFile, plugin) => rewriteBody(raw.replace(/\r\n/g, "\n"), relFile, plugin);

const writeComponent = (srcFile, destFile, plugin) =>
  fs.writeFileSync(destFile, normalizeComponent(fs.readFileSync(srcFile, "utf8"), path.relative(SRC, srcFile), plugin));

const copyDir = (srcDir, plugin, destSub) => {
  const dest = path.join(OUT, plugin, destSub);
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(srcDir, { withFileTypes: true })) {
    const s = path.join(srcDir, entry.name);
    if (entry.isDirectory()) { copyDir(s, plugin, path.join(destSub, entry.name)); continue; }
    const d = path.join(dest, entry.name);
    const rel = path.relative(SRC, s);
    if (entry.name === "SKILL.md") fs.writeFileSync(d, normalizeComponent(fs.readFileSync(s, "utf8"), rel, plugin));
    else if (entry.name.endsWith(".md")) fs.writeFileSync(d, normalizeReference(fs.readFileSync(s, "utf8"), rel, plugin));
    else fs.copyFileSync(s, d);
  }
};

preflight();
for (const [name, plugin] of Object.entries(SKILLS))
  copyDir(path.join(SRC, "skills", name), plugin, path.join("skills", name));
for (const [name, plugin] of Object.entries(AGENTS)) {
  fs.mkdirSync(path.join(OUT, plugin, "agents"), { recursive: true });
  writeComponent(path.join(SRC, "agent", `${name}.md`), path.join(OUT, plugin, "agents", `${name}.md`), plugin);
}
for (const [name, plugin] of Object.entries(COMMANDS)) {
  fs.mkdirSync(path.join(OUT, plugin, "commands"), { recursive: true });
  writeComponent(path.join(SRC, "workflows", `${name}.md`), path.join(OUT, plugin, "commands", `${name}.md`), plugin);
}
fs.mkdirSync(".tmp", { recursive: true });
fs.writeFileSync(".tmp/cross-plugin-flags.txt", flags.join("\n") + "\n");
console.log(`Converted ${Object.keys(SKILLS).length} skills, ${Object.keys(AGENTS).length} agents, ${Object.keys(COMMANDS).length} commands. Flags: ${flags.length} (see .tmp/cross-plugin-flags.txt).`);
