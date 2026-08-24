---
description: Create a comprehensive marketing campaign from strategy to execution.
---

# /campaign - Create Marketing Campaign

> **Lead agent:** this workflow is driven by the `marketing-strategist` agent (this plugin) — delegate the phases below to it, pulling in other marketing agents/skills as noted.

Follow this workflow to create a marketing campaign.

## Step 1: Campaign Brief

Define the campaign basics:

1. **Goal**: What are we trying to achieve?
   - Awareness
   - Lead generation
   - Sales/conversions
   - Product launch
   - Brand building

2. **Target Audience**: Who are we reaching?
   - Demographics
   - Psychographics
   - Pain points
   - Where they hang out

3. **Budget & Timeline**: Resources and deadlines

4. **Success Metrics**: How will we measure success?

## Step 2: Strategy Development

1. **Positioning**: How do we want to be perceived?
2. **Messaging**: Key messages and value proposition
3. **Channels**: Which channels to use
   - Paid (Google, Meta, LinkedIn)
   - Organic (SEO, social, email)
   - Earned (PR, influencers)
4. **Creative direction**: Visual and copy themes

## Step 3: Content Creation

Create campaign assets (for any single asset, you can run `/aak-marketing:content` to go brief→research→outline→write→optimize):

1. **Landing pages**: Design and copy
2. **Ad creative**: Images, videos, copy
3. **Email sequences**: Nurture flows
4. **Social content**: Platform-specific posts
5. **Blog/SEO content**: Supporting content

## Step 4: Setup & Launch

1. **Tracking**: UTMs, pixels, conversion events
2. **Audience setup**: Targeting configuration
3. **A/B tests**: Variations to test
4. **Launch checklist**: Pre-flight checks
5. **Go live**: Execute launch

## Step 5: Optimize

1. **Monitor**: Daily/weekly check-ins
2. **Analyze**: Performance vs goals
3. **Iterate**: Adjust based on data
4. **Report**: Share learnings

## Output

- Campaign brief document
- Content calendar
- Creative assets
- Tracking setup
- Results report

## Step 6: Presentation Builder (optional)

Ask the user whether they want an HTML presentation deck for this campaign. If yes:

### 6.1 Build the deck
Use the **`frontend-slides` skill** (this plugin) to build a single-file HTML presentation:
- Slide-based navigation (arrow keys + click), progress bar, mobile swipe.
- All CSS inline (no external dependencies); pick fonts that render the content's language correctly.
- Slides: title, goals & KPIs, audience, key messaging, channels, timeline, content plan, success metrics, next steps.
- Save to `docs/campaign-presentation.html`.

### 6.2 Preview locally
Open the file in a browser (`open` / `xdg-open` / `start` depending on OS), or serve the `docs/` folder with `python3 -m http.server`.

### 6.3 Share (optional)
To share, deploy the static HTML to any static host the user already uses (e.g. GitHub Pages, Netlify, Vercel), or send the file directly. Only expose a local tunnel with the user's explicit consent — do not open the user's machine to the public by default.

## Step 7: Automated video production (optional)

Ask the user whether they want automated video ads (TikTok / Reels / Meta). If yes, use the **`video-automation`** and **`remotion-best-practices`** skills (this plugin):
- Take a natural-language brief (e.g. "a 9:16 TikTok promoting feature X, neon style" or "a 16:9 and a 9:16 cut of this campaign").
- Build the Remotion composition, preview locally (the skill provides the dev-server command), then render to MP4 (the skill checks for FFmpeg and installs it if missing).
- Define your own composition IDs per format (e.g. one for 16:9, one for 9:16) — do not reuse example IDs from other projects.

## Skills used

- `content-marketing`, `copywriting` — messaging & asset copy (Step 3)
- `page-cro` / `conversion-optimization` — landing pages (Step 3)
- `email-marketing` — nurture sequences (Step 3)
- `social-media-expert` — social content (Step 3)
- `analytics-marketing` — tracking & measurement (Steps 4–5)
- `frontend-slides` — presentation deck (Step 6)
- `video-automation`, `remotion-best-practices` — video ads (Step 7)
