---
description: Convene a simulated board of legendary marketing advisors to debate a marketing decision and synthesize a recommendation.
---

# /council - Marketing Council

> **Decide direction before executing.** Seats advisors whose documented frameworks
> deliberately collide (Godin, Ogilvy, Schwartz, Dunford, Hormozi, Sharp, Sutherland, …),
> maps where they disagree, and ends with a chair's synthesis that hands off to the
> execution skills.

This command runs the `marketing-council` skill (in `aak-marketing`).

## Step 1: Gather inputs
- The decision or work product under review (strategy, landing page, pricing change,
  launch plan, rebrand, ad account) and what's at stake / already tried.
- Session mode: quick take (1 named advisor), council session (3–5, default), or full
  council (all 12 — only when stakes justify it). Honor any advisors the user names.
- Optional: `.agents/product-marketing.md` — the shared positioning/ICP/voice doc (created by
  the `product-marketing` skill). If present, the council reads it instead of re-asking.

## Step 2: Run the session
Follow the `marketing-council` skill: seat the bench (always at least one designated
dissenter), load only the seated advisors' dossiers, run the optional live research pass
when the question is specific or time-sensitive, then produce each take, the disagreement
map, and the chair's synthesis. Label the output as simulation; no fabricated quotes.
Produce the session in-conversation (no filesystem writes unless the user adds a custom
advisor, which is saved to `.agents/advisors/<name>.md`).

## Handoffs
- `/aak-marketing:marketing-plan` — turn the chosen direction into a sequenced plan.
- `/aak-marketing:campaign` · `/aak-marketing:content` · `/aak-marketing:optimize` —
  execute the winning direction.
