---
name: vision-analysis
description: >
  Analyze, describe, and extract information from images using Claude's native image understanding.
  Use when: user shares an image file path or URL (any message containing .jpg, .jpeg, .png,
  .gif, .webp, .bmp, or .svg file extension) or uses any of these words/phrases near an image:
  "analyze", "analyse", "describe", "explain", "understand", "look at", "review",
  "extract text", "OCR", "what is in", "what's in", "read this image", "see this image",
  "tell me about", "explain this", "interpret this", in connection with an image, screenshot,
  diagram, chart, mockup, wireframe, or photo.
  Also triggers for: UI mockup review, wireframe analysis, design critique, data extraction
  from charts, object detection, person/animal/activity identification.
  Triggers: any message with an image file extension (jpg, jpeg, png, gif, webp, bmp, svg),
  or any request to analyze/describ/understand/review/extract text from an image, screenshot,
  diagram, chart, photo, mockup, or wireframe.
license: MIT
metadata:
  version: "1.0"
  category: ai-vision
  sources:
    - Claude native vision (Read tool)
    - Optional fallback: MiniMax Token Plan MCP (understand_image tool)
---

# Vision Analysis

Analyze images using **Claude's native image understanding** — Claude Code reads image files
directly, so no external vision API is required. (Adapted from the antigravity-marketing
`vision-analysis` skill, which routed to the paid MiniMax vision tool; that path is preserved
as an optional fallback below for hosts without native vision.)

## Prerequisites

- **None.** Claude reads images natively via the `Read` tool on the image file path.
- Optional: a vision MCP (e.g. MiniMax) only if you run this on a host with no native vision — see the fallback section at the end.

## Analysis Modes

| Mode | When to use | Prompt strategy |
|---|---|---|
| `describe` | General image understanding | Ask for detailed description |
| `ocr` | Text extraction from screenshots, documents | Ask to extract all text verbatim |
| `ui-review` | UI mockups, wireframes, design files | Ask for design critique with suggestions |
| `chart-data` | Charts, graphs, data visualizations | Ask to extract data points and trends |
| `object-detect` | Identify objects, people, activities | Ask to list and locate all elements |

## Workflow

### Step 1: Auto-detect image

The skill triggers automatically when a message contains an image file path or URL with extensions:
`.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, `.svg`

Extract the image path from the message.

### Step 2: Read the image and apply the mode prompt

**Use the `Read` tool on the image path** — Claude sees the image directly. Then analyze it
using the mode-specific prompt below:

**describe:**
```
Provide a detailed description of this image. Include: main subject, setting/background,
colors/style, any text visible, notable objects, and overall composition.
```

**ocr:**
```
Extract all text visible in this image verbatim. Preserve structure and formatting
(headers, lists, columns). If no text is found, say so.
```

**ui-review:**
```
You are a UI/UX design reviewer. Analyze this interface mockup or design. Provide:
(1) Strengths — what works well, (2) Issues — usability or design problems,
(3) Specific, actionable suggestions for improvement. Be constructive and detailed.
```

**chart-data:**
```
Extract all data from this chart or graph. List: chart title, axis labels, all
data points/series with values if readable, and a brief summary of the trend.
```

**object-detect:**
```
List all distinct objects, people, and activities you can identify. For each,
describe what it is and its approximate location in the image.
```

### Step 3: Present results

Return the analysis clearly. For `describe`, use readable prose. For `ocr`, preserve structure. For `ui-review`, use a structured critique format.

## Output Format Example

For describe mode:
```
## Image Description

[Detailed description of the image contents...]
```

For ocr mode:
```
## Extracted Text

[Preserved text structure from the image]
```

For ui-review mode:
```
## UI Design Review

### Strengths
- ...

### Issues
- ...

### Suggestions
- ...
```

## Notes

- Common raster and vector formats are supported (JPEG, PNG, GIF, WebP, BMP, SVG).
- Local file paths work directly with the `Read` tool.
- Only fall back to an external vision MCP when the running host has no native image support.

---

## Fallback: external vision MCP (optional)

If you run this skill on a host **without** native vision, you can route to the MiniMax
`MiniMax_understand_image` MCP tool instead (requires a MiniMax Token Plan + `MINIMAX_API_KEY`):

**Claude Code**:
```bash
claude mcp add -s user MiniMax --env MINIMAX_API_KEY=your-key --env MINIMAX_API_HOST=https://api.minimaxi.com -- uvx minimax-coding-plan-mcp -y
```

Then call `MiniMax_understand_image` with the same mode-specific prompts above. Setup guide:
https://platform.minimaxi.com/docs/token-plan/mcp-guide
