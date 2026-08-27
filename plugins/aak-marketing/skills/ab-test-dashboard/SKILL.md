---
name: ab-test-dashboard
description: Own the full A/B experiment lifecycle — design (hypothesis, test types, guardrail metrics, traffic allocation, client-vs-server, peeking), sizing & significance (power/MDE), tracking dashboards, and results reporting. Use for planning, running, or analyzing an A/B test or experiment. Triggers on A/B test, split test, experiment, statistical significance, hypothesis, sample size, test dashboard. (CRO opportunity-finding & prioritization stays in conversion-optimization, which hands the test itself to this skill.)
allowed-tools: Read, Glob, Grep
---

# A/B Test Dashboard

> Track experiments, measure results, and make data-driven decisions.

---

## 🎯 What This Skill Does

| Capability | Description |
|------------|-------------|
| **Design Tests** | Structure proper A/B experiments |
| **Track Results** | Monitor test performance |
| **Calculate Stats** | Statistical significance checks |
| **Visualize Data** | Dashboard creation |
| **Report Findings** | Communicate results clearly |

---

## 1. A/B Test Basics

### What is an A/B Test?

| Term | Meaning |
|------|---------|
| **Control (A)** | Your current version |
| **Variant (B)** | The change you're testing |
| **Sample size** | Number of visitors needed |
| **Significance** | Confidence results aren't random |
| **Conversion** | The action you're measuring |

### What to Test (Priority)

| High Impact | Medium Impact | Low Impact |
|-------------|---------------|------------|
| Headlines | Button text | Font size |
| CTAs | Images | Colors |
| Pricing | Form fields | Spacing |
| Offers | Layout | Icons |
| Landing pages | Navigation | Animations |

---

## 2. Sample Size Calculator

### Quick Formula

```
Sample Size = (Z² × p × (1-p)) / E²

Where:
- Z = 1.96 for 95% confidence
- p = expected conversion rate
- E = margin of error (±)
```

### Simple Reference Table

| Current Rate | Lift to Detect | Sample per Variation |
|--------------|----------------|----------------------|
| 1% | 20% | ~40,000 |
| 2% | 20% | ~20,000 |
| 5% | 20% | ~8,000 |
| 10% | 15% | ~4,000 |
| 20% | 10% | ~3,000 |

### Online Calculators

| Tool | URL |
|------|-----|
| **Optimizely** | optimizely.com/sample-size-calculator |
| **AB Tasty** | abtasty.com/sample-size-calculator |
| **Evan Miller** | evanmiller.org/ab-testing/sample-size |

---

## 3. Dashboard Metrics

### Core Metrics to Track

| Metric | Formula |
|--------|---------|
| **Conversion Rate** | Conversions / Visitors × 100 |
| **Relative Lift** | (B - A) / A × 100 |
| **Confidence Level** | Statistical p-value calculation |
| **Visitors per Day** | Total visitors / Days running |
| **Days to Significance** | Required sample / Daily visitors |

### Dashboard Layout

```
┌─────────────────────────────────────────────┐
│  TEST: [Name]                Status: RUNNING │
├─────────────────────────────────────────────┤
│                                             │
│   Control (A)        Variant (B)            │
│   ┌─────────┐       ┌─────────┐            │
│   │  2.5%   │       │  3.1%   │            │
│   │  Conv   │       │  Conv   │            │
│   └─────────┘       └─────────┘            │
│                                             │
│   Visitors: 5,432    Visitors: 5,489       │
│   Conversions: 136   Conversions: 170      │
│                                             │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      │
│   Lift: +24%    Confidence: 87%            │
│   ⚠️ Not yet significant (need 95%)        │
│                                             │
├─────────────────────────────────────────────┤
│  Progress: ████████░░░░░░ 68% complete      │
│  Est. completion: 4 more days               │
└─────────────────────────────────────────────┘
```

---

## 4. Statistical Significance

### What Does It Mean?

| Confidence | Meaning |
|------------|---------|
| **95%** | α = 5%: ≤5% chance of a false positive when there is no real difference (standard) |
| **99%** | α = 1%: ≤1% false-positive rate (high stakes) |
| **90%** | α = 10%: ≤10% false-positive rate (quick tests) |

### Quick Significance Check

| Scenario | Likely Significant? |
|----------|---------------------|
| Big difference + many visitors | ✅ Yes |
| Small difference + few visitors | ❌ No |
| Big difference + few visitors | ⚠️ Wait |
| Small difference + many visitors | ⚠️ Maybe real, but small |

### Avoid Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Stopping early | False positives | Wait for sample size |
| Peeking too much | Bias decisions | Set check schedule |
| Testing too many things | Can't attribute cause | One change at a time |
| Running too short | Misses weekly patterns | Run 1-2 full weeks |

---

## 5. Simple Dashboard with Google Sheets

### Setup Steps

```
1. Create new Google Sheet
2. Tab 1: Raw data (date, variant, visitors, conversions)
3. Tab 2: Summary calculations
4. Tab 3: Charts
```

### Formula Examples

| Metric | Google Sheets Formula |
|--------|----------------------|
| **Conversion Rate A** | `=SUMIF(B:B,"A",D:D)/SUMIF(B:B,"A",C:C)` |
| **Conversion Rate B** | `=SUMIF(B:B,"B",D:D)/SUMIF(B:B,"B",C:C)` |
| **Lift** | `=(B_Rate-A_Rate)/A_Rate` |
| **Daily Visitors** | `=SUMIF(A:A,TODAY()-1,C:C)` |

### Simple Significance Formula

```
For approximation (use proper calculator for real tests):

Z = (pB - pA) / SQRT(p*(1-p)*(1/nA + 1/nB))

Where:
- pA, pB = conversion rates
- p = pooled rate = (convA + convB) / (nA + nB)
- nA, nB = sample sizes

If |Z| > 1.96, result is significant at 95%
```

---

## 6. Test Documentation

### Pre-Test Template

```markdown
## Test: [Name]

### Hypothesis
If we [change], then [metric] will [improve] because [reason].

### Test Details
- Page/Element: 
- Control: [Description]
- Variant: [Description]
- Primary metric: 
- Secondary metrics:

### Sample Size
- Current conversion rate: X%
- Minimum detectable effect: Y%
- Required visitors per variant: Z

### Timeline
- Start date:
- Expected end date:
- Check-in dates:
```

### Post-Test Template

```markdown
## Test Results: [Name]

### Summary
- Winner: [Control/Variant/No difference]
- Confidence: X%
- Lift: +/-Y%

### Data
| Metric | Control | Variant | Lift |
|--------|---------|---------|------|
| Visitors | | | |
| Conversions | | | |
| Conv Rate | | | |

### Learning
What did we learn?

### Next Steps
- Implement winner?
- Follow-up test?
- Share with team?
```

---

## 7. Tools for A/B Testing

### Free/Cheap Tools

| Tool | Best For | Cost |
|------|----------|------|
| **Google Optimize** | Websites (sunset, but alternatives exist) | Free |
| **Splitbee** | Simple tests | Free tier |
| **Growthbook** | Open source | Free |
| **Posthog** | Feature flags + analytics | Free tier |

### Paid Tools

| Tool | Best For | Cost |
|------|----------|------|
| **VWO** | Full CRO platform | $199+/mo |
| **Optimizely** | Enterprise | $$$$ |
| **AB Tasty** | Mid-market | $$$ |
| **Convert** | SMB friendly | $99+/mo |

---

## 8. Visualization Best Practices

### Chart Types

| Data | Chart Type |
|------|------------|
| Rate comparison | Bar chart |
| Trend over time | Line chart |
| Sample progress | Progress bar |
| Segment breakdown | Pie/donut |
| Confidence range | Error bars |

### Dashboard Colors

| Status | Color |
|--------|-------|
| Winning (significant) | Green |
| Losing (significant) | Red |
| Running (not significant) | Yellow/Gray |
| Winner | Blue (neutral) |

---

> **Remember:** Statistical significance ≠ practical significance. Always ask: "Is this lift worth the effort to implement?"

---

## Full experiment lifecycle & reference guides

This skill owns the whole experiment lifecycle: **design → size → run → measure → report**. Load on demand:

- `references/test-design-guide.md` — hypothesis framework, test types (A/B, A/B/n, MVT, split-URL), guardrail metrics, traffic allocation/ramping, client-vs-server-vs-feature-flag, and the peeking problem.
- `references/statistical-guide.md` — **canonical** sizing & significance method: prefer the power + MDE sample-size formula `n = 2·((z_α + z_β)² · p·(1-p)) / MDE²` (it accounts for statistical power, unlike the quick margin-of-error approximation shown earlier) and the duration formula `Days = (sample size per variant × variants) / daily traffic`.

CRO opportunity-finding, hypotheses, and ICE/PIE prioritization live in **conversion-optimization**, which hands the actual test off to this skill; event/tracking instrumentation lives in the analytics skills.
