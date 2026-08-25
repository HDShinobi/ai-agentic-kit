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

Score each dimension **0–100** against the **observable criteria** below — each dimension carries six equally-weighted checks (~17 pts each). Only score what you can actually see on the page or what the user provided. **If a dimension can't be assessed from available evidence, mark it `Unknown` — do not invent a number.**

| Dimension | Lead skill / agent | Score on these observable criteria (each ~17 pts) |
|-----------|--------------------|---------------------------------------------------|
| **Content & Messaging** | `content-creator` · copywriting | Value prop clear in ≤5s · benefit-led (not feature-led) · customer language · one idea per section · scannable · specific (no vague hype) |
| **Conversion** | `growth-specialist` · page-cro | Use the `page-cro` *Readiness Index* six categories (value-prop clarity, goal focus, traffic–message match, trust signals, friction/UX, objection handling), rescaled to 0–100 |
| **SEO & Discoverability** | `seo-specialist` · seo-fundamentals + geo-fundamentals | Title/meta present & sized · H1 + heading hierarchy · image alt coverage · canonical/robots/sitemap · schema markup · GEO signals (FAQ, cited stats, author) |
| **Brand & Trust** | brand / branding-expert | Consistent visual identity · clear positioning · social proof present · claims substantiated · contact/about legitimacy · risk reducers at decision points |
| **Competitive Positioning** | competitor-teardown | Differentiation stated · category clarity · unique value vs. alternatives · proof of superiority · pricing transparency · switching-cost/moat signals |
| **Growth & Strategy** | `growth-specialist` · `marketing-strategist` | Clear next step/funnel entry · lead capture · activation path · retention hooks · referral/virality · measurable acquisition channel |

> **Degradation rule:** delegate a dimension to its specialist only if that agent's plugin is enabled; otherwise perform the analysis inline with the same skill's framework. Never reference an agent that isn't reachable.

> **Machine signals vs. verdict:** the `analyze_page.py` output is a coarse **0–10 heuristic signal** (`heuristic_signal_0_to_10`), NOT a dimension score. Use it as *evidence* feeding the SEO/Conversion/Trust criteria above — never copy it in as the 0–100 score.

## Step 3: Compute the overall score

- **Overall Marketing Score = average of the dimensions you could actually score (0–100).** Exclude any `Unknown` dimension from the average — never treat missing evidence as 0 or 100.
- Report **coverage** (e.g. "5 of 6 dimensions scored") and an overall **confidence** (high/medium/low) based on how much was directly observed vs. inferred.
- Flag each dimension's band: <55 Not-ready · 55–69 Low · 70–84 Moderate · 85+ High.
- Be honest and specific. **No fabricated metrics, benchmarks, or testimonials** — cite only what the page actually shows or what the user provided. Where you estimate, label it an estimate and give a range with its basis.

## Step 4: Prioritize fixes

Rank recommendations by **impact × ease**:

1. **Quick wins** — high impact, low effort (do this week).
2. **Foundations** — high impact, higher effort (structural fixes before testing).
3. **Experiments** — worth A/B testing once foundations are solid.

## Step 5: Output the report

Write **`MARKETING-AUDIT.md`** in the project root:

1. **Header** — URL, date, **Overall Marketing Score /100**.
2. **Scorecard** — each dimension with its score (or `Unknown`), band, and one-line verdict; plus coverage ("N of 6 scored") and overall confidence.
3. **Findings** — per dimension: what's working, what's costing conversions/traffic, why it matters.
4. **Prioritized fixes** — quick wins → foundations → experiments.
5. **Suggested next step** — hand off to the right workflow.

## Handoffs

- `/aak-marketing:optimize` — execute the conversion fixes.
- `/aak-marketing:seo` — deep SEO/GEO pass.
- `/aak-marketing:report` or `/aak-marketing:brand-report` — turn the audit into a polished client-ready PDF.
- `client-proposal` skill — turn audit findings into a data-backed proposal.
- `/aak-marketing:campaign` — if the fix is a whole go-to-market, not one page.
