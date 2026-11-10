<!-- KIT NOTE — added by ai-agentic-kit, NOT upstream. -->
> **Source.** Grafted byte-verbatim from `arnabbagxd/Brand-building-skills` (MIT, © 2026 Arnab Bag), `skills/aso/SKILL.md` lines 102, 117–121, 159, 169–173, 186–207, commit `4a0a8b5`. Extracts are separated by `<!-- extract -->` markers; text between markers is unchanged upstream bytes.
>
> **⚠️ Platform mechanics change.** Apple Product Page Optimization and Google Play Store Listing
> Experiments limits (treatment counts, durations, splits) and review-prompt rules are as stated by the
> upstream author at time of writing — verify against current App Store Connect / Play Console docs
> before planning a test. Complements this skill's `ab_test_planner.py`.
>
> **⚠️ Two upstream inaccuracies (kept verbatim below, corrected here).** (1) There is no
> "SKStoreReviewRequestAPI": the iOS API is StoreKit's `SKStoreReviewController.requestReview` /
> SwiftUI `requestReview` action. (2) Apple shows the system rating prompt at most **three times per
> 365 days** per user (not once) — and the system may decline to show it, so never tie UX to it appearing.
>
> Upstream content is preserved verbatim below.

### 03 — DESCRIPTION OPTIMIZATION

<!-- extract -->

**Description rules:**
- iOS: The App Store description does NOT directly affect search ranking (keywords here don't count for iOS ASO). Focus on conversion.
- Google Play: Description DOES affect ranking. Include keywords naturally throughout.
- Use line breaks and emoji to aid scannability
- Keep paragraphs to 2–3 sentences max

<!-- extract -->

### 05 — RATINGS AND REVIEW STRATEGY

<!-- extract -->

**In-app rating prompt (most important):**
- Use SKStoreReviewRequestAPI (iOS) — only shows Apple's native prompt
- Trigger at a positive moment: after completing a task, after a session streak, after a positive interaction
- Do NOT trigger after errors, purchases, or frustrating moments
- Prompt once per 365 days maximum (Apple's limit)

<!-- extract -->

### 06 — A/B TESTING ON THE APP STORE

**What to test:**
- App icon (biggest impact on browse discovery)
- Screenshot 1 (hero frame and headline)
- Screenshot order
- Preview video vs. no video
- Dark vs. light mode screenshots

**How to test:**

**iOS (Product Page Optimization):**
- Available in App Store Connect
- Test up to 3 treatments vs. control
- Minimum 90 days for statistical significance
- Only visible to users who find the app in App Store (not existing users)

**Google Play (Store Listing Experiments):**
- Available in Google Play Console
- Test icon, screenshots, short description, long description
- Set traffic split (recommend 50/50)
- Run for minimum 7 days, ideally 30+
