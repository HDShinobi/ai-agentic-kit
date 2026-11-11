---
name: deck
description: Slide-content orchestrator. Routes a deck request through storyline, ghost deck, action titles, opening and ask pages, chart exhibits, and review, calling this plugin's skills in order and stopping for approval before slide copy is written. Use when the user wants to write, plan, restructure, or review the content of a deck, board pack, client readout, or internal update. Not for rendering or converting slide files. Triggers on deck storyline, slide content, ghost deck, board pack, action titles, slide exhibit, so-what title, review my deck.
---

# Deck: slide-content router

This skill owns the **content** of a deck: the argument, the titles, the pages, and the
exhibits. It does not draw slides. Rendering is handed off at the end (Step 9).

## Scope

- **In scope:** decks that inform a decision or carry an argument: board packs, client
  readouts, steering-committee and internal updates, recommendation or proposal decks,
  results reviews (for example a campaign or ad-account performance review).
- The sibling skills are written for board packs. Read "the board" as whoever must
  decide or act on this deck, and "partner" as the most senior reviewer before it goes out.
- **Sales or pitch decks** (selling to a prospect): if the `aak-marketing` plugin is
  enabled, invoke its `sales-enablement` skill for the deck framework, then return here
  for Steps 3 and 5, then Steps 6–9. If it is not enabled, proceed with this flow.

## Modes

Pick the mode from the request. When invoked as `/deck <word> …` and the first word is one
of `plan`, `write`, `titles`, `chart`, or `review`, use it as the mode. With no arguments,
start at Step 0. Ask only if the mode is genuinely ambiguous.

| The user wants… | Mode | Runs |
|---|---|---|
| A new deck from material, notes, or data | `plan` then `write` | Steps 0–9 |
| Only the storyline / outline agreed | `plan` | Steps 0–2 |
| Slide copy for an agreed outline | `write` | Steps 3–9 |
| Better titles on an existing deck | `titles` | Step 3, then 7–8 |
| A chart that makes its point | `chart` | Step 5 |
| A check before sending | `review` | Step 6, then 7–8 |

**Every mode first collects whichever Step 0 items its skills need and are missing**
(for example the governing thought for `titles`, the audience and decision for `chart` and
`review`, the language for Steps 7–8). Do not re-ask for items already given.

## Flow

### Step 0: Brief
Collect, in one message, only what is missing:
- **Audience:** who reads or hears it, and what they already know.
- **Decision or action:** what they should decide, approve, or do afterward.
- **Material:** data, notes, prior decks, constraints (page count, time slot, template).
- **Format:** presented live or sent as a pre-read. A pre-read needs denser pages.
- **Language:** the output language (see Step 8).

### Step 1: Storyline
Invoke `board-narrative-scqa`: governing thought, SCQA, and the pyramid of supporting points.

### Step 2: Ghost deck (approval gate)
Invoke `ghost-deck-skeleton`. It writes each slide's action title and exhibit sketch. Show
the user the title-only read of the ghost deck and **stop for approval**. Do not write slide
copy or build exhibits until the storyline and page list are agreed. Revisions loop back to
Step 1 or Step 2. Exhibit sketches here are provisional; Step 5 may change the chart type.

### Step 3: Action titles
- **After an approved ghost deck:** invoke `action-title-writer` as a verification pass.
  Change only titles that fail its tests or the title-only read, and show each change as
  before → after. Approved titles that pass stay as they are.
- **In `titles` mode on an existing deck:** invoke `action-title-writer` on every title,
  then show the title-only read of the result.

### Step 4: Opening and closing pages
- Invoke `executive-summary-page` for the page that opens the deck.
- If the deck asks for a decision, approval, budget, or go/no-go, invoke
  `decision-and-ask-page` for the page that closes it.

### Step 5: Exhibits
For each slide whose exhibit is quantitative data, run in order:
1. `chart-type-selection` (may override the ghost deck's provisional sketch)
2. `waterfall-and-bridge-charts` when the message is how a value moved from A to B
3. `chart-to-message-mapper`
4. `color-encoding-for-data`
5. `data-ink-reducer` (last pass)

For each slide whose point is a structure (2x2, value chain, process, roadmap), invoke
`framework-slide-designer`.

### Step 6: Review
Invoke `partner-review-checklist` on the full deck. Apply the fixes in its priority order,
and loop back to the step that owns each fix. On a content-only spec (not yet rendered),
mark the slide-craft items (grid, spacing, icons, visual consistency) as not assessable, and
re-run those items after rendering.

### Step 7: AI-tell pass
If the `aak-core` plugin's `humanizer` skill is available, run it on all slide text
(titles, body, exhibit labels). It must not change numbers, claims, or the ask. If it is not
available, proceed normally.

### Step 8: Language
If the deck is in Vietnamese and the `aak-vietnamese` plugin is enabled, invoke the matching
`vietnamese-*` skill (`vietnamese-business-comms` for client or sales decks,
`vietnamese-tech-writing` for technical or internal decks, `vietnamese-finance-copy` for
financial content). If it is not enabled, proceed normally.

### Step 9: Hand-off to rendering
Deliver the content as a slide-by-slide spec: number, action title, body, exhibit spec.
Then, if the user wants a file:
- If the `aak-marketing` plugin is enabled, its `frontend-slides` skill builds an HTML deck
  (with PPTX export).
- Otherwise, if a PPTX-building skill is available in the session (for example a `pptx`
  skill), hand the spec to it.
- If none is available, the slide-by-slide spec is the deliverable.

## Rules
- One message per slide. If a slide needs two points, it becomes two slides.
- The title-only read of the deck must tell the whole story. Re-check after every revision.
- Never invent data to fill an exhibit. Mark missing data in the exhibit spec and list it
  for the user.
- Run only the steps the mode needs. Do not run the full flow for a titles-only request.
