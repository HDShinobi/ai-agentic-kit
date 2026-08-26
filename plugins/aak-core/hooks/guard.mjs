#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

// Collapse `X/../` traversal so paths that resolve to root are caught
// (e.g. "/tmp/../" -> "/", "/var/.." -> "/"). Leading "/" is preserved.
function normalizePath(tok) {
  const abs = tok.startsWith("/");
  const tilde = tok.startsWith("~");
  const body = tilde ? tok.slice(1) : tok;
  const parts = body.split("/").filter((p) => p !== "" && p !== ".");
  const out = [];
  for (const p of parts) {
    if (p === "..") { if (out.length) out.pop(); }
    else out.push(p);
  }
  if (tilde) return "~" + (out.length ? "/" + out.join("/") : "");
  if (abs) return "/" + out.join("/");
  return out.join("/");
}

// Reduce one segment to its effective command + args:
// strip sudo/doas/env prefixes, then unwrap `sh -c <cmd>` style shell wrappers.
function unwrap(s) {
  let prev;
  do {
    prev = s;
    s = s.replace(/^(?:sudo\s+|doas\s+|env\s+\S+=\S+\s+|[A-Za-z_][A-Za-z0-9_]*=\S+\s+)+/, "");
    // shell -c wrapper: the command lives after the -c flag
    const m = s.match(/^(?:\S*\/)?(?:sh|bash|zsh|dash|ash|ksh)\s+(?:-\S+\s+)*-c\s+(.*)$/i);
    if (m) s = m[1].trim();
  } while (s !== prev);
  return s;
}

// Basename of the first token (strips a leading path: "/bin/rm" -> "rm").
function verb(s) {
  const first = s.split(" ")[0] || "";
  return first.replace(/^.*\//, "");
}

export function isDestructive(command) {
  // Split on shell operators AND command-substitution boundaries `$( ) ` `` ` ``
  // so a destructive command nested inside a substitution is scanned on its own.
  for (const rawSeg of String(command).split(/(?:\|\||&&|[;&|\n]|\$\(|\)|`)+/)) {
    let s = unwrap(rawSeg.replace(/["']/g, " ").replace(/\s+/g, " ").trim());
    const v = verb(s);
    if (v === "rm") {
      const rec   = /(?:^|\s)-[a-z]*r|--recursive/i.test(s);
      const force = /(?:^|\s)-[a-z]*f|--force/i.test(s);
      const root = s.split(" ").slice(1).some((t) => {
        if (/^-/.test(t)) return false; // skip flags
        const p = normalizePath(t.replace(/^\$\{?HOME\}?/i, "~"));
        return /^(\/|\/\*|~|[A-Za-z]:\\?)$/.test(p);
      });
      if (rec && force && root) return true;
    }
    if (/^mkfs(\.\w+)?$/i.test(v) && /\/dev\//i.test(s)) return true;
    if (v === "dd" && /\bof=\/dev\/(?:sd|nvme|disk|rdisk|hd|mmcblk|vd|xvd)/i.test(s)) return true;
    if (v === "format" && /^format\s+[A-Za-z]:/i.test(s)) return true;
    if (/^Remove-Item$/i.test(v) && /-Recurse\b/i.test(s) && /-Force\b/i.test(s)
        && /(?:^|\s)[A-Za-z]:\\?(?=\s|$)/i.test(s)) return true;
  }
  return false;
}

// CLI: only runs when executed directly, not when imported by the test
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  let raw = ""; try { raw = readFileSync(0, "utf8"); } catch { process.exit(0); }
  // Fail-closed: if the payload is malformed JSON we cannot extract the command
  // cleanly, so scan the raw text rather than silently allowing it through.
  let cmd = "";
  try { cmd = JSON.parse(raw || "{}")?.tool_input?.command ?? ""; }
  catch { cmd = raw; }
  if (cmd && isDestructive(cmd)) {
    console.error("BLOCKED by AI Agentic Kit: refusing a high-confidence destructive command.");
    process.exit(2);
  }
  process.exit(0);
}
