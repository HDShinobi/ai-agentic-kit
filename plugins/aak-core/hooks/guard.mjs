#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

export function isDestructive(command) {
  for (const seg of String(command).split(/(?:\|\||&&|[;&|\n])+/)) {
    let s = seg.replace(/["']/g, " ").replace(/\s+/g, " ").trim();
    s = s.replace(/^(?:sudo\s+|doas\s+|env\s+\S+=\S+\s+|[A-Za-z_][A-Za-z0-9_]*=\S+\s+)+/, ""); // strip sudo/env
    if (/^rm\b/i.test(s)) {
      const rec   = /(?:^|\s)-[a-z]*r|--recursive/i.test(s);
      const force = /(?:^|\s)-[a-z]*f|--force/i.test(s);
      const root  = /(?:^|\s)(\/|\/\*|~\/?|\$\{?HOME\}?\/?|[A-Za-z]:\\?)(?=\s|$)/i.test(s);
      if (rec && force && root) return true;
    }
    if (/^mkfs(\.\w+)?\b/i.test(s) && /\/dev\//i.test(s)) return true;
    if (/^dd\b/i.test(s) && /\bof=\/dev\/(?:sd|nvme|disk|rdisk|hd|mmcblk|vd|xvd)/i.test(s)) return true;
    if (/^format\b\s+[A-Za-z]:/i.test(s)) return true;
    if (/^Remove-Item\b/i.test(s) && /-Recurse\b/i.test(s) && /-Force\b/i.test(s)
        && /(?:^|\s)[A-Za-z]:\\?(?=\s|$)/i.test(s)) return true;
  }
  return false;
}

// CLI: only runs when executed directly, not when imported by the test
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  let raw = ""; try { raw = readFileSync(0, "utf8"); } catch { process.exit(0); }
  let payload = {}; try { payload = JSON.parse(raw || "{}"); } catch { process.exit(0); }
  const cmd = payload?.tool_input?.command ?? "";
  if (cmd && isDestructive(cmd)) {
    console.error("BLOCKED by AI Agentic Kit: refusing a high-confidence destructive command.");
    process.exit(2);
  }
  process.exit(0);
}
