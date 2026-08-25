---
name: audit
description: Full marketing audit of a website — score content, conversion, SEO/GEO, competitive positioning, brand, and growth into one client-ready report, and track before/after across re-runs.
---

# /audit - Marketing Audit

> **Lead agent:** `marketing-strategist` (this plugin) runs on the main thread, fans out each dimension to the matching specialist, and synthesizes one scored report. Methodology, weights, rubrics, and the report format live in the **`site-audit` skill** (this plugin) — follow it exactly.

**Target:** $ARGUMENTS

## Step 1: Gather evidence (don't guess)

Use the `site-audit` skill's Phase 1 (discovery + business-type detection). For measured signals, run the bundled analyzer:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/site-audit/scripts/analyze_page.py" <url>
```

It returns JSON (title/meta, headings, CTA count, forms, trust/social links, tracking, schema, alt-text gaps) plus a coarse `heuristic_signal_0_to_10` — treat that as **evidence**, not the score. Only public URLs are scanned; to audit your own localhost/staging set `AAK_ALLOW_PRIVATE_URLS=1`. If the URL can't be reached, ask for pasted content rather than inventing findings. Also read the page directly with available web tooling.

## Step 2: Score the six dimensions against the rubrics

Delegate each dimension to its specialist **if that plugin/agent is enabled, else do it inline** (degradation rule — never reference an unreachable agent). Each specialist loads and applies its rubric file **literally**:

| Dimension | Agent | Rubric (in `site-audit` skill) |
|-----------|-------|--------------------------------|
| Content & Messaging | `content-creator` | `rubrics/content.md` |
| Conversion | `growth-specialist` | `rubrics/conversion.md` |
| SEO & Discoverability | `seo-specialist` | `rubrics/seo.md` |
| Competitive Positioning | `marketing-strategist` | `rubrics/competitive.md` |
| Brand & Trust + Growth & Strategy | `analytics-specialist` / `marketing-strategist` | `rubrics/strategy.md` |

Each returns a structured result: **{observation, source (URL/quote), score 0–100, confidence, evidence-gaps}**. If a dimension can't be assessed from available evidence, return `Unknown` — do not invent a number.

## Step 3: Aggregate

Apply the weighted score from the `site-audit` skill (Content .25 · Conversion .20 · SEO .20 · Competitive .15 · Brand .10 · Growth .10). **Exclude any `Unknown` dimension** from the weighted average (renormalize weights over what was scored) and report **coverage** ("N of 6 scored") + overall **confidence**. Honesty rule: cite only what the page shows or the user provided; label any estimate as an estimate with its basis. Do not fabricate metrics, benchmarks, or revenue numbers.

## Step 4: Write the report + persist history (money-loop)

1. Write **`MARKETING-AUDIT.md`** in the project root using the `site-audit` skill's report template (score breakdown, quick wins, strategic, long-term).
2. **Persist a dated copy**: also save `audits/<YYYY-MM-DD>-<domain-slug>.md` (create `audits/` if missing). This is what makes the loop longitudinal — pass today's date in; never guess it.
3. **Delta (if a prior audit exists):** if `audits/` already holds an earlier report for this domain, compare per-dimension scores and add a **"Change since last audit"** section (e.g. Content 62 → 81) — the before/after proof for a client/retainer.

## Handoffs

- `client-proposal` skill — turn the audit's scored gaps into a priced, data-backed proposal.
- `/aak-marketing:optimize` — execute the conversion fixes.
- `/aak-marketing:seo` — deep SEO/GEO pass.
- `/aak-marketing:report` or `/aak-marketing:brand-report` — render the audit as a polished client PDF.
- `/aak-marketing:campaign` — if the fix is a whole go-to-market, not one page.
