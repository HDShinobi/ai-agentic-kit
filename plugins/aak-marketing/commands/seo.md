---
name: seo
description: Run an SEO/GEO audit or optimization pass — technical SEO, on-page, E-E-A-T, Core Web Vitals, keyword strategy, and AI-search (GEO) visibility.
---

# /seo - SEO & GEO Optimization

> **Lead agent:** driven by the `seo-specialist` agent (this plugin). Pull in the SEO/GEO skills below.

$ARGUMENTS

Optimize a site/page for search and AI-answer engines. Work through the relevant phases:

## Step 1: Scope
What's the target (site, section, or specific page) and the goal (rankings, organic traffic, AI-search citations, technical fixes)?

## Step 2: Audit
- **Technical**: crawlability, indexation, sitemaps, structured data (schema), Core Web Vitals (LCP/INP/CLS). → skill `seo-fundamentals`.
- **On-page**: titles, meta, headings, internal links, E-E-A-T signals. → skill `seo-fundamentals`.
- **AI-search (GEO)**: is the content structured to be cited by ChatGPT/Perplexity/Gemini? → skill `geo-fundamentals`.

## Step 3: Keyword & content strategy
- Intent-mapped keyword research, clustering, gaps, long-tail. → skill `keyword-research-deep`.
- At scale (templated pages over a dataset)? Assess feasibility first. → skill `programmatic-seo`.

## Step 4: Prioritize & report
Rank findings by impact × effort; output an actionable list (Issue → Impact → Fix → Priority). For a styled PDF, hand off to `/aak-marketing:report`.

## Skills used
`seo-fundamentals`, `geo-fundamentals`, `keyword-research-deep`, `programmatic-seo` — all in this plugin.
