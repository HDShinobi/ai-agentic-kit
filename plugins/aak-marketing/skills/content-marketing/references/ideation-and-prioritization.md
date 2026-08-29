# Content Ideation & Prioritization

<!-- KIT NOTE — added by ai-agentic-kit, NOT upstream. -->
> **⚠️ Directional single-vendor study.** The Link-Earning Formats table (Foundation Inc. "4.25x" statistics-roundup figure and the rest of the multipliers) comes from one vendor's B2B SaaS backlink study — treat the numbers as directional, not universal. The *ranking* of formats is a useful prior; the exact multipliers will vary by industry and audience.
> **ℹ️ Two different splits — not a contradiction.** This file's Prioritizing weights and the source skill's **60/30/10** calendar split (searchable / shareable / experimental) describe a *distribution of pieces across intent types*. The content-marketing body's **70-20-10** Content-Mix rule (core / evolution / experimental) is a *different axis* — proven vs. new topics. They measure different things and can both hold at once.
> Upstream content is preserved verbatim below.

## Content Ideation Sources

### 1. Keyword Data

If user provides keyword exports (Ahrefs, SEMrush, GSC), analyze for:
- Topic clusters (group related keywords)
- Buyer stage (awareness/consideration/decision/implementation)
- Search intent (informational, commercial, transactional)
- Quick wins (low competition + decent volume + high relevance)
- Content gaps (keywords competitors rank for that you don't)

Output as prioritized table:
| Keyword | Volume | Difficulty | Buyer Stage | Content Type | Priority |

### 2. Call Transcripts

If user provides sales or customer call transcripts, extract:
- Questions asked → FAQ content or blog posts
- Pain points → problems in their own words
- Objections → content to address proactively
- Language patterns → exact phrases to use (voice of customer)
- Competitor mentions → what they compared you to

Output content ideas with supporting quotes.

### 3. Survey Responses

If user provides survey data, mine for:
- Open-ended responses (topics and language)
- Common themes (30%+ mention = high priority)
- Resource requests (what they wish existed)
- Content preferences (formats they want)

### 4. Forum Research

Use web search to find content ideas:

**Reddit:** `site:reddit.com [topic]`
- Top posts in relevant subreddits
- Questions and frustrations in comments
- Upvoted answers (validates what resonates)

**Quora:** `site:quora.com [topic]`
- Most-followed questions
- Highly upvoted answers

**Other:** Indie Hackers, Hacker News, Product Hunt, industry Slack/Discord

Extract: FAQs, misconceptions, debates, problems being solved, terminology used.

### 5. Competitor Analysis

Use web search to analyze competitor content:

**Find their content:** `site:competitor.com/blog`

**Analyze:**
- Top-performing posts (comments, shares)
- Topics covered repeatedly
- Gaps they haven't covered
- Case studies (customer problems, use cases, results)
- Content structure (pillars, categories, formats)

**Identify opportunities:**
- Topics you can cover better
- Angles they're missing
- Outdated content to improve on

### 6. Sales and Support Input

Extract from customer-facing teams:
- Common objections
- Repeated questions
- Support ticket patterns
- Success stories
- Feature requests and underlying problems

---

## Prioritizing Content Ideas

Score each idea on four factors:

### 1. Customer Impact (40%)
- How frequently did this topic come up in research?
- What percentage of customers face this challenge?
- How emotionally charged was this pain point?
- What's the potential LTV of customers with this need?

### 2. Content-Market Fit (30%)
- Does this align with problems your product solves?
- Can you offer unique insights from customer research?
- Do you have customer stories to support this?
- Will this naturally lead to product interest?

### 3. Search Potential (20%)
- What's the monthly search volume?
- How competitive is this topic?
- Are there related long-tail opportunities?
- Is search interest growing or declining?

### 4. Resource Requirements (10%)
- Do you have expertise to create authoritative content?
- What additional research is needed?
- What assets (graphics, data, examples) will you need?

### Scoring Template

| Idea | Customer Impact (40%) | Content-Market Fit (30%) | Search Potential (20%) | Resources (10%) | Total |
|------|----------------------|-------------------------|----------------------|-----------------|-------|
| Topic A | 8 | 9 | 7 | 6 | 8.0 |
| Topic B | 6 | 7 | 9 | 8 | 7.1 |

Score 1-10 per factor, multiply by the weight, sum for the total. Rank the list; make the top-scoring pieces first.

---

### Link-Earning Formats

When the goal of a piece is backlinks specifically, format choice matters more than production effort. Foundation Inc.'s B2B Backlink Intelligence Report (March 2026 — a single vendor study of B2B SaaS sites, so treat as directional) measured each format's share of backlinks relative to its share of pages:

| Format | Backlinks vs. page share |
|---|---|
| Statistics / data roundups | **4.25x** |
| Glossary / definition pages | 1.47x |
| Interactive tools / calculators (see **free-tool-strategy**) | 1.38x |
| How-to / tutorials | 1.36x |
| Original research / reports | 0.80x |
| Ultimate guides | 0.77x |
| Thought leadership | 0.74x |
| Templates / frameworks | 0.68x |

The counterintuitive read: **curating statistics earns ~5x the links of producing original research.** Writers link to whatever makes citation easiest — a maintained stat-roundup page is citation infrastructure, while original research often gets cited *via* the roundups that aggregate it. Implications: (1) publish a stats page for your category and keep it fresh — it's cheap and compounds, and citable one-line stats are also what LLMs lift, making it an AI-visibility play (see **geo-fundamentals**); (2) when you do run original research, pair it with your own stat-roundup page that presents the findings as citable one-liners, so you capture the links your data generates. The formats at the bottom aren't dead — guides, templates, and thought leadership earn their keep on rankings, conversions, and brand. Judge each piece by the job it's for, and don't expect links from formats that don't earn them.

For programmatic content at scale, see **programmatic-seo** skill.
