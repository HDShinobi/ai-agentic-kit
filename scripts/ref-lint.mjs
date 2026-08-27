#!/usr/bin/env node
// ref-lint.mjs — catches hollow references that `claude plugin validate` does NOT.
//
// Two checks across every plugin under plugins/:
//   1. name-mismatch : a skill's frontmatter `name:` must equal its directory name.
//   2. retired-alias : no .md may reference a retired/renamed skill name (dead cross-refs).
//
// Exit code 1 if any finding, so it can gate CI / run alongside `claude plugin validate`.
// Usage:  node scripts/ref-lint.mjs

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, basename, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(fileURLToPath(new URL('.', import.meta.url)), '..');
const PLUGINS = join(ROOT, 'plugins');

// Retired/renamed skill names that must never appear as a cross-reference again.
// Map each to its live replacement (for a helpful message). Extend when a skill is renamed.
const RETIRED = {
  'ab-test-setup': 'ab-test-dashboard',
  'seo-audit': 'seo-fundamentals',
  'analytics-tracking': 'analytics-marketing',
  'competitor-teardown-agent': 'competitor-teardown',
  'competitor-monitor-alert': 'competitor-monitor',
  'content-repurposing-pipeline': 'content-repurposing',
};

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) walk(p, out);
    else if (name.endsWith('.md')) out.push(p);
  }
  return out;
}

function frontmatterName(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return null;
  const line = m[1].split('\n').find((l) => /^name:\s*/.test(l));
  return line ? line.replace(/^name:\s*/, '').trim().replace(/^["']|["']$/g, '') : null;
}

const findings = [];
const files = walk(PLUGINS);

for (const f of files) {
  const text = readFileSync(f, 'utf8');
  const rel = relative(ROOT, f);

  // Check 1: skill name must match its directory name.
  if (basename(f) === 'SKILL.md') {
    const dir = basename(join(f, '..'));
    const name = frontmatterName(text);
    if (name && name !== dir) {
      findings.push(`name-mismatch  ${rel}: frontmatter name "${name}" != dir "${dir}"`);
    }
  }

  // Check 2: no references to retired skill names (word-boundary).
  const lines = text.split('\n');
  for (const [alias, live] of Object.entries(RETIRED)) {
    const re = new RegExp(`\\b${alias}\\b`, 'g');
    lines.forEach((ln, i) => {
      // A skill's own frontmatter `name:` line is exempt (it IS the definition, not a ref);
      // but retired names should never be a definition either, so we still flag them.
      if (re.test(ln)) findings.push(`retired-alias  ${rel}:${i + 1}: "${alias}" -> use "${live}"`);
    });
  }
}

if (findings.length) {
  console.error(`ref-lint: ${findings.length} finding(s)\n` + findings.map((x) => '  ' + x).join('\n'));
  process.exit(1);
}
console.log(`ref-lint: OK (${files.length} .md files scanned, no hollow refs or name mismatches)`);
