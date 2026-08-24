// One-time importer: adopt curated marketing skills into aak-marketing VERBATIM,
// normalizing only frontmatter (drop dead fields, merge when_to_use, strip Agent/Antigravity
// tools, strip ckm: name prefix) and flagging cross-references for a manual link-audit.
// Content of every skill is copied unchanged. Mirrors scripts/convert.mjs.
import fs from "node:fs";
import path from "node:path";

const AM = ".tmp/antigravity-marketing/templates/.agent/skills";
const MM = ".tmp/minimax-skills/skills";
const OUT = "plugins/aak-marketing/skills";
const flags = [];

// name -> source root. All adopted skills land in aak-marketing/skills/<name>/.
const FROM_AM = [
  // CRO
  "conversion-optimization","page-cro","popup-cro","signup-flow-cro","onboarding-cro","paywall-upgrade-cro",
  // SEO
  "keyword-research-deep","programmatic-seo",
  // Content
  "content-marketing","content-repurposing","copywriting",
  // Email / lifecycle
  "email-marketing","marketing-automation",
  // Analytics
  "analytics-marketing","ab-test-dashboard",
  // Growth / monetization
  "growth-hacking","launch-strategy","referral-program","pricing-strategy","marketing-ideas","marketing-psychology",
  // Brand / competitor
  "branding-expert","competitor-teardown","competitor-monitor",
  // Channels
  "ppc-advertising","ad-creative-variations","social-media-expert","influencer-marketing","affiliate-marketing","video-marketing","app-store-optimization","lead-gen-scraper",
  // Slides / video production
  "frontend-slides","remotion-best-practices","video-automation","tutorial-video-expert",
  // Claudekit
  "brand","banner-design",
  // Viral (Apache)
  "viral-generator-builder",
];
const FROM_MM = ["minimax-pdf"];

const DROP_KEYS = ["version","requires_agents","requires_skills","artifact_outputs","priority","effort","metadata","trigger","skills","argument-hint","risk","source","sources","author","date_added","license"];

const splitFrontmatter = (raw) => {
  const text = raw.replace(/\r\n/g, "\n");
  if (!text.startsWith("---\n")) return { hasFm: false, body: text };
  const end = text.indexOf("\n---\n", 4);
  if (end < 0) return { hasFm: false, body: text };
  const fm = {}; const order = []; const block = {}; let cur = null;
  for (const line of text.slice(4, end).split("\n")) {
    if (line.trim() === "") continue;
    if (/^\s/.test(line)) { if (cur === null) throw new Error(`stray indent: ${line}`); block[cur].push(line); continue; }
    const mm = line.match(/^([A-Za-z0-9_-]+):\s?(.*)$/);
    if (!mm) throw new Error(`unparseable fm line: ${line}`);
    const [, k, v] = mm; fm[k] = v; order.push(k);
    // A key with empty value OR a folded/literal marker (| >) may be followed by indented lines.
    if (v.trim() === "" || /^[|>][+-]?$/.test(v.trim())) { cur = k; block[k] = []; } else cur = null;
  }
  // Resolve indented blocks: nested mapping (all children look like `key: val`) → keep in `block`
  // (dropped/handled by rebuild). Otherwise it's a folded/literal SCALAR → join into fm[key].
  for (const k of Object.keys(block)) {
    const kids = block[k];
    if (kids.length === 0) continue;
    const isMapping = kids.every((l) => /^\s+[A-Za-z0-9_-]+:\s/.test(l));
    if (!isMapping) { fm[k] = kids.map((l) => l.trim()).join(" "); delete block[k]; }
  }
  return { hasFm: true, fm, body: text.slice(end + 5), order, block };
};
const unquote = (v) => String(v).replace(/^["'](.*)["']$/s, "$1");
const needsQuote = (v) => /[:#]/.test(v) || /^\s|\s$/.test(v) || /^[>|&*!%@`"'\[\]{},]/.test(v);
const emit = (k, v) => { const r = unquote(v); return needsQuote(r) ? `${k}: "${r.replace(/"/g, '\\"')}"` : `${k}: ${r}`; };
const rebuild = (fm, order, block) =>
  "---\n" + order.filter((k) => !DROP_KEYS.includes(k) && fm[k] !== undefined)
    .map((k) => (block[k] && block[k].length) ? (()=>{throw new Error(`block key kept: ${k}`)})() : emit(k, fm[k]))
    .join("\n") + "\n---\n";

const flagRefs = (body, rel) => body.split("\n").forEach((line, i) => {
  for (const m of line.matchAll(/\.agents\/\S+|\.claude\/skills\/\S+|ckm:|ai-artist|ai-multimodal|browser_subagent|design-system\/scripts/g))
    flags.push(`${rel}:${i + 1}\t${m[0]}`);
});

const normalizeSkill = (raw, rel) => {
  const fmr = splitFrontmatter(raw);
  if (!fmr.hasFm) { flagRefs(fmr.body, rel); return fmr.body; }
  const { fm, body, order, block } = fmr;
  if (fm.when_to_use !== undefined) {
    fm.description = `${unquote(fm.description || "")} ${unquote(fm.when_to_use)}`.trim();
    if (!order.includes("description")) order.splice(order.indexOf("when_to_use"), 0, "description");
    delete fm.when_to_use;
  }
  if (fm.name) fm.name = unquote(fm.name).replace(/^ckm:/, "");            // strip claudekit prefix
  for (const tk of ["tools", "allowed-tools"])
    if (fm[tk] !== undefined) fm[tk] = fm[tk].split(",").map(s=>s.trim()).filter(t=>t && t!=="Agent" && t!=="ViewCodeItem" && t!=="FindByName").join(", ");
  flagRefs(body, rel);
  return rebuild(fm, order, block) + body;
};

const copyDir = (src, dst) => {
  fs.mkdirSync(dst, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name), d = path.join(dst, e.name);
    if (e.isDirectory()) { copyDir(s, d); continue; }
    if (e.name === "SKILL.md") fs.writeFileSync(d, normalizeSkill(fs.readFileSync(s, "utf8"), path.relative(".", s)));
    else fs.copyFileSync(s, d);
  }
};

let n = 0;
for (const [root, list] of [[AM, FROM_AM], [MM, FROM_MM]])
  for (const name of list) {
    const src = path.join(root, name);
    if (!fs.existsSync(path.join(src, "SKILL.md"))) { console.error(`SKIP (no SKILL.md): ${src}`); continue; }
    copyDir(src, path.join(OUT, name)); n++;
  }
fs.mkdirSync(".tmp", { recursive: true });
fs.writeFileSync(".tmp/marketing-import-flags.txt", [...new Set(flags)].sort().join("\n") + "\n");
console.log(`Imported ${n} skills into ${OUT}. Ref-flags: ${new Set(flags).size} (see .tmp/marketing-import-flags.txt).`);
