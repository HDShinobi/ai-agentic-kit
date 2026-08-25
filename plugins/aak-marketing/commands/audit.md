---
name: audit
description: Full marketing audit of a website — score content, conversion, SEO/GEO, brand, competitive positioning, and growth, then output a prioritized, client-ready report.
---

# /audit - Marketing Audit

> **Lead agent:** driven by the `marketing-strategist` agent (this plugin). It runs on the main thread and fans out each dimension below to the matching specialist, then synthesizes one scored report. (Subagents can't spawn subagents, so the strategist coordinates from the main thread.)

Audit the target and produce a single scored report with concrete fixes.

**Target:** $ARGUMENTS

## Step 1: Gather real page signals (don't guess)

Pull actual data about the page before scoring:

1. If Python is available, run the bundled analyzer for structured signals (title, meta, headings, CTAs, forms, trust/social links, tracking, schema, image alt coverage):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/page-cro/scripts/analyze_page.py" <url>
   ```
   It prints JSON — use it as evidence, not as the verdict.
2. Otherwise, fetch the page with whatever web tooling is available and read the rendered content directly.
3. If the URL can't be reached, ask the user to paste the page content or a screenshot rather than inventing findings.

## Step 2: Score six dimensions (delegate if the plugin is enabled, else inline)

Score each **0–100**. For **Conversion**, use the `page-cro` skill's *Page Conversion Readiness & Impact Index*; for the rest, apply the matching skill's framework.

| Dimension | Lead skill / agent | Looks at |
|-----------|--------------------|----------|
| **Content & Messaging** | `content-creator` · copywriting | Value-prop clarity, benefit-led copy, customer language |
| **Conversion** | `growth-specialist` · page-cro / conversion-optimization | CTA focus, friction, trust signals, objection handling |
| **SEO & Discoverability** | `seo-specialist` · seo-fundamentals + geo-fundamentals | Technical + on-page SEO, structured data, AI-search (GEO) |
| **Brand & Trust** | brand / branding-expert | Consistency, credibility, social proof |
| **Competitive Positioning** | competitor-teardown | Differentiation vs. alternatives |
| **Growth & Strategy** | `growth-specialist` · `marketing-strategist` | Funnel, acquisition/retention leverage, next-best-bets |

> **Degradation rule:** delegate a dimension to its specialist only if that agent's plugin is enabled; otherwise perform the analysis inline with the same skill's framework. Never reference an agent that isn't reachable.

## Step 3: Compute the overall score

- **Overall Marketing Score = average of the six dimension scores (0–100).**
- Flag each dimension's band (e.g. page-cro: <55 Not-ready · 55–69 Low · 70–84 Moderate · 85+ High).
- Be honest and specific. No fabricated metrics, benchmarks, or testimonials — cite only what the page actually shows or what the user provided. Where you estimate, say so and give a range.

## Step 4: Prioritize fixes

Rank recommendations by **impact × ease**:

1. **Quick wins** — high impact, low effort (do this week).
2. **Foundations** — high impact, higher effort (structural fixes before testing).
3. **Experiments** — worth A/B testing once foundations are solid.

## Step 5: Output the report

Write **`MARKETING-AUDIT.md`** in the project root:

1. **Header** — URL, date, **Overall Marketing Score /100**.
2. **Scorecard** — the six dimensions with score, band, and a one-line verdict each.
3. **Findings** — per dimension: what's working, what's costing conversions/traffic, why it matters.
4. **Prioritized fixes** — quick wins → foundations → experiments.
5. **Suggested next step** — hand off to the right workflow.

## Handoffs

- `/aak-marketing:optimize` — execute the conversion fixes.
- `/aak-marketing:seo` — deep SEO/GEO pass.
- `/aak-marketing:report` or `/brand-report` — turn the audit into a polished client-ready PDF.
- `client-proposal` skill — turn audit findings into a data-backed proposal.
- `/aak-marketing:campaign` — if the fix is a whole go-to-market, not one page.
