---
description: Turn marketing content, analysis, or proposals into a professional, print-ready PDF report.
---

# /report - Professional PDF Report

Use this workflow to turn marketing content, analysis results, or proposals into a high-quality PDF, using the `minimax-pdf` skill (this plugin).

## Step 1: Pick a report type
Choose a preset for the right design:
- `report` — metrics report, modern, table-heavy
- `proposal` — project proposal, formal
- `resume` — CV / expert profile
- `portfolio` — visual project showcase
- `magazine` — image-rich magazine layout
- `minimal` — clean, minimal design

## Step 2: Prepare the content
1. **Title** — the report's main title.
2. **Author** — person or team.
3. **Content** — structured text: headings (H1/H2/H3), body, bullet points, results (tables/charts).

## Step 3: Refine the design
1. **Accent color** — a brand-appropriate HEX (e.g. `#2D5F8A` tech, `#2E5E3A` sustainability).
2. **Cover image** — provide a path or a description for the cover.

## Step 4: Generate the PDF
Use the `minimax-pdf` skill to render:
1. Assemble the data into `content.json`.
2. Run the generation command (see the skill).
3. Verify the output (`out.pdf`).

## Output
- A professional, print-ready PDF for clients or stakeholders.
- Styled cover, auto table of contents, and refined layout.

## Skills used
- `minimax-pdf` — PDF generation (this plugin)
- An image-analysis skill (optional) — only if you need to analyze a cover image; use whatever vision/image skill is available in your environment.
