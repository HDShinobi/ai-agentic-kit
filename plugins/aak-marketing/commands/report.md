---
description: Workflow to create professional PDF reports from HTML/Markdown.
---

# /report - Professional PDF Report

Use this workflow to turn marketing content, analysis results, or proposals into a high-quality PDF file.

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
Use the `minimax-pdf` tool to render:
1. Assemble the data into `content.json`.
2. Run the report-generation command.
3. Verify the output file (`out.pdf`).

## Output
- A professional PDF, ready to print or send to clients.
- A report with a nice cover, auto table of contents, and refined layout.

## Skills Used
- minimax-pdf
- vision-analysis (if you need to analyze the cover image)
