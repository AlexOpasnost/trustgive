# TrustGive — Changelog

All notable decisions, agent actions, and artifact changes are logged here in chronological order.

---

## [2026-05-05] [Project Lead] [Phase 0 — Intake]

- Conducted intake interview (Block 1 + Block 2)
- User chose to delegate Block 3 (technical scope) and Block 5 (budget detail) to agents — market research drives feature decisions
- **Locked decisions**:
  - Problem: people struggle to find charities they can trust
  - Target: global donors (English + Russian primary languages)
  - Core action: **find** a verified charity (then redirect to charity's own site)
  - Platform: **Web-first** (responsive React); mobile deferred to post-MVP
  - **No payment processing** — TrustGive is a discovery layer
  - Differentiators: (1) deeper verification transparency, (2) stronger filters, (3) no money-handling
  - Budget: $0/month (free tiers only)
- **Project name**: `trustgive`
- **Files created**:
  - `projects/trustgive/SPEC.md` — v0.1 draft, awaits Market Analyst input for final
  - `projects/trustgive/CHANGELOG.md` — this file
  - `projects/trustgive/PHASE_STATE.md` — Phase 0 in progress, transitioning to Phase 1
- **Next**: Activate Market Analyst (Phase 1) with expanded scope: competitors, feature demand, anti-features, verification sources, promotion strategy, MVP build sequence

---

## [2026-05-05] [Market Analyst] [Phase 1 — Market Research]

- Analyzed 12 competitors (Charity Navigator, GiveWell, GlobalGiving, JustGiving, Candid/GuideStar, CharityWatch, BBB Give.org, Effektiv-Spenden, Благо.ру, VK Добро, Нужна помощь, Every.org)
- Captured 6 Playwright screenshots (saved to `.claude/.playwright-mcp/trustgive-*.png`)
- Mined feature-demand signals from Trustpilot, Reddit, EA Forum, donor research reports
- **Key findings**:
  - 3 free APIs unlock $0-budget MVP: **ProPublica Nonprofit Explorer** (1.8M US orgs, no key), **Every.org Charity API** (cause taxonomy + 1M+ orgs), **CharityBase.uk** (168K UK orgs)
  - Top anti-feature in market: hidden default tips (JustGiving's #1 Trustpilot complaint) — TrustGive avoids this by design
  - Nobody covers "show me the source documents" well — TrustGive's wedge
  - No platform shows RU charities to EN-speaking donors with verification proof — bilingual gap
- **Recommendations integrated**:
  - MVP scope: US + UK auto-loaded + 30 hand-curated RU charities
  - NO accounts in MVP, NO AI recommender, NO user reviews (legal/noise risk), NO email digest (RSS instead)
  - Positioning: "the only charity discovery tool that shows you the source documents"
  - Launch channels: PH + Show HN + r/EffectiveAltruism + EA Forum + Indie Hackers + LinkedIn build-in-public
  - 8-week build sequence with W2 alpha / W4 beta / W8 public launch
- **Files created**:
  - `projects/trustgive/MARKET_ANALYSIS.md` — full report
  - `knowledge-base/by-role/market-analyst/lessons-learned.md` — KB-MARKET-TRUSTGIVE-001 (free nonprofit APIs)
  - `knowledge-base/by-role/shared/common-pitfalls.md` — AP-SHARED-009 (conflicting agent/harness instructions)
- **Reflection**: Hybrid Playwright + WebSearch approach worked under sandbox restrictions. Free APIs in civic tech are under-publicized — ProPublica is the best-kept secret. Charity Navigator's 2023 abandonment of overhead-ratio scoring is a strategic opportunity gap.
- **Next**: User approval (Gate 0 + Gate 1 combined) → revise SPEC.md to v1.0 → Phase 2 (Designer)

---

## [2026-05-05] [Project Lead] [Gate 0 + Gate 1 — APPROVED]

- User approved combined Gate 0 (intake) + Gate 1 (market research) with "продолжаем"
- **Decisions locked**:
  - Geo MVP scope: US (auto via ProPublica + Every.org) + UK (auto via CharityBase) + 30 RU (manual curation)
  - **No accounts, no AI, no user reviews, no email digest** in MVP (v1)
  - Positioning: "show you the source documents — not a star rating you can't audit"
  - 8-week build sequence with W2 alpha / W4 closed beta / W7 soft launch / W8 PH+HN public launch
  - Promotion: Product Hunt → Show HN → r/EA + EA Forum → Indie Hackers → LinkedIn build-in-public
- **Files modified**:
  - `projects/trustgive/SPEC.md` — promoted v0.1 → v1.0; closed all 7 open questions; added 6 user stories with Gherkin acceptance criteria; finalized integrations table
  - `projects/trustgive/PHASE_STATE.md` — Gate 0+1 marked approved
  - `projects/trustgive/PROJECTS.md` — status to In Progress, phase to Phase 2
- **Next**: Phase 2 (Designer) — UI/UX research via Playwright, color palette, typography, wireframes for catalog/detail/methodology pages. Cost Tracker logging Phase 0+1 in parallel.
