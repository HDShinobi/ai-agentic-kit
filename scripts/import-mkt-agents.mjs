// Adopt the 4 marketing agents + 6 marketing workflows into aak-marketing, normalizing frontmatter.
import fs from "node:fs";
import path from "node:path";
const SRC = ".tmp/antigravity-marketing/templates/.agent";
const AGENTS = ["marketing-strategist", "content-creator", "growth-specialist", "analytics-specialist"];
const WORKFLOWS = ["campaign", "content", "optimize", "analyze", "report", "brand-report"];
const DROP = ["version","requires_agents","requires_skills","artifact_outputs","priority","effort","metadata","trigger","skills","argument-hint","risk","source","sources","author","date_added","license"];

const norm = (raw) => {
  const t = raw.replace(/\r\n/g, "\n");
  if (!t.startsWith("---\n")) return t;
  const end = t.indexOf("\n---\n", 4);
  if (end < 0) return t;
  const fm = {}, order = [], block = {}; let cur = null;
  for (const line of t.slice(4, end).split("\n")) {
    if (line.trim() === "") continue;
    if (/^\s/.test(line)) { if (cur !== null) block[cur].push(line); continue; }
    const m = line.match(/^([A-Za-z0-9_-]+):\s?(.*)$/); if (!m) continue;
    fm[m[1]] = m[2]; order.push(m[1]);
    if (m[2].trim() === "" || /^[|>][+-]?$/.test(m[2].trim())) { cur = m[1]; block[m[1]] = []; } else cur = null;
  }
  for (const k of Object.keys(block)) { const kids = block[k]; if (kids.length && !kids.every(l => /^\s+[A-Za-z0-9_-]+:\s/.test(l))) { fm[k] = kids.map(l => l.trim()).join(" "); delete block[k]; } }
  if (fm.when_to_use !== undefined) { const uq = s => String(s).replace(/^["'](.*)["']$/s, "$1"); fm.description = `${uq(fm.description||"")} ${uq(fm.when_to_use)}`.trim(); if (!order.includes("description")) order.splice(order.indexOf("when_to_use"), 0, "description"); delete fm.when_to_use; }
  for (const tk of ["tools", "allowed-tools"]) if (fm[tk] !== undefined) fm[tk] = fm[tk].split(",").map(s => s.trim()).filter(x => x && x !== "Agent" && x !== "ViewCodeItem" && x !== "FindByName").join(", ");
  const uq = s => String(s).replace(/^["'](.*)["']$/s, "$1");
  const nq = v => /[:#]/.test(v) || /^\s|\s$/.test(v) || /^[>|&*!%@`"'\[\]{},]/.test(v);
  const emit = (k, v) => { const r = uq(v); return nq(r) ? `${k}: "${r.replace(/"/g, '\\"')}"` : `${k}: ${r}`; };
  const head = "---\n" + order.filter(k => !DROP.includes(k) && fm[k] !== undefined && !(block[k] && block[k].length)).map(k => emit(k, fm[k])).join("\n") + "\n---\n";
  return head + t.slice(end + 5);
};

fs.mkdirSync("plugins/aak-marketing/agents", { recursive: true });
fs.mkdirSync("plugins/aak-marketing/commands", { recursive: true });
for (const a of AGENTS) fs.writeFileSync(`plugins/aak-marketing/agents/${a}.md`, norm(fs.readFileSync(`${SRC}/agents/${a}.md`, "utf8")));
for (const w of WORKFLOWS) fs.writeFileSync(`plugins/aak-marketing/commands/${w}.md`, norm(fs.readFileSync(`${SRC}/workflows/${w}.md`, "utf8")));
console.log(`Imported ${AGENTS.length} agents + ${WORKFLOWS.length} commands into aak-marketing.`);
