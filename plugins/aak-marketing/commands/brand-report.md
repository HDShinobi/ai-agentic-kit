---
description: Generate a report whose design is "cloned" from a brand's website, from just a URL.
---

# /brand-report - Brand-Styled Report

> **Output tooling** (not a strategy step): a variant of `/report` that clones a brand's visual style from its website before rendering the PDF.

Use this workflow to produce a report that visually matches a company's brand, given only their website URL.

## "One-prompt" flow

Provide the request in this shape:
> "Run /brand-report for the data in [file] using the style of [website URL]"

### Steps the AI performs:

1.  **Crawl the brand**: use an available browser tool (`chrome-devtools` MCP, `playwright` MCP, or `ego-browser`) to visit the site and extract:
    - The official logo.
    - The signature palette (primary, secondary colors).
    - Fonts and design style (dark / light mode).

2.  **Design the layout**: apply the above into a coherent report design system — use the `ui-ux-pro-max` skill (if available), or the `brand` / `frontend-design` skills.

3.  **Process the data**: read the input file and convert it into professional content blocks (charts, tables, callouts).

4.  **Render the PDF**: use the `minimax-pdf` skill (this plugin) to render the final high-quality PDF.

## Example

**Input**:
- File: `marketing_results_q1.txt`
- Website: `https://www.tesla.com`

**Result**: a PDF report with Tesla's logo on the cover, its signature red/black/white palette, a modern minimal typeface, and charts rendered in the brand colors.

## Skills / tools used

- This command orchestrates the steps above directly (no external orchestrator skill needed).
- `minimax-pdf` skill — PDF rendering (this plugin)
- A browser tool — crawl brand (chrome-devtools / playwright / ego-browser)
- `ui-ux-pro-max` (if available) or `brand` / `frontend-design` — design system
