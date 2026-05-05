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

---

## [2026-05-05] [Cost Tracker] [Phase 0+1 logged]

- Logged 3 sessions for trustgive: Phase 0 ($1.17), Phase 1 ($2.96), Phase 0+1 finalization ($1.95)
- **Project total: $6.08 / $200 budget (3.0% used)** · ~189,690 tokens (Opus 4.7 standard tier)
- Files updated: `costs/COSTS.md`, `PROJECTS.md` (root), `knowledge-base/by-role/cost-tracker/lessons-learned.md`
- KB entry added: KB-COST-TRUSTGIVE-001 (HIGH severity) — Opus 4.7 1M context two-tier pricing rule
- Optimization recs for next phases: Sonnet 4.6 for docs/devops phases (~5x savings)
- Note: Cost Tracker subagent had Write blocked; Project Lead applied changes manually

---

## [2026-05-05] [Designer] [Phase 2 — Design]

- Researched 8 design references: Stripe Press, NYT Open + NYT.com, Charity:Water (anti-pattern), Effektiv-Spenden (methodology + home), Linear, Vercel, Are.na — plus Charity Navigator as anti-pattern reference
- ⚠️ **Note**: Playwright `browser_take_screenshot` was sandbox-blocked — no design-research PNGs saved. Visual analysis was done via navigate-only reads. URLs preserved in DESIGN.md §12 for human re-verification
- Produced `DESIGN.md` v1.0 — full design system:
  - 6 design principles (documents over ratings, restraint over emphasis, numbers as first-class, dignity not pity, bilingual at byte 1, methodology-as-homepage)
  - Semantic color tokens (light + dark) with **WCAG AA contrast computed per pair** — every text/bg combination ≥ 4.5:1
  - Type scale: **Inter (sans) + Source Serif 4 (serif) + Geist Mono** — verified Cyrillic-complete $0-budget triplet
  - Lucide icons, 4-px spacing, 8/12 radius, no shadows (1px rules)
  - 9 component patterns (top nav, filter sidebar, charity card, charity detail, donate-modal, methodology page, source-document drawer, comparison view, empty/loading/error states)
  - 6 key-screen wireframes (homepage, catalog, charity detail, comparison, SEO landing, methodology)
  - Motion + a11y + brand mini-kit
- **Key opinionated decisions** (open for revision at Gate 2):
  1. Forest green `#0E7C5C` as trust accent — differentiates from Charity Navigator/GuideStar/BBB (all navy)
  2. Wordmark-only logo in v1 (no symbol-logo until v2)
  3. **Zero photography of people across the entire site** — strongest brand differentiator
  4. Source-document drawer is the over-designed wedge interaction
- **Component library**: shadcn/ui + Radix primitives + TailwindCSS v4 + Recharts (all MIT/free)
- **Files created**: `projects/trustgive/DESIGN.md`
- **KB entries added** (3) to `knowledge-base/by-role/designer/lessons-learned.md`:
  - KB-DESIGNER-TRUSTGIVE-001 (MEDIUM) — Bilingual EN+RU font triplet
  - KB-DESIGNER-TRUSTGIVE-002 (MEDIUM) — "Trust UI" anti-pattern: ban photography of people
  - KB-DESIGNER-TRUSTGIVE-003 (LOW) — Off-white paper requires per-pair WCAG re-audit
- **Reflection**: research-discipline (8 deep refs > 30 shallow) paid off; for bilingual products, font choice is single biggest decision; for trust UIs, photography policy is stronger differentiator than palette
- **Next**: Awaiting Gate 2 user approval → Phase 2.5 (Backend Developer for API design + ADRs)

---

## [2026-05-05] [Project Lead] [Infra Setup — GitHub]

- Initialized git in `projects/trustgive/` (main branch)
- Created `.gitignore` (Django + React + Flutter + IDE/OS) + `README.md` (build-in-public landing)
- Two commits pushed:
  - `9baf71f` Initial commit (SPEC, MARKET_ANALYSIS, CHANGELOG, PHASE_STATE, README, .gitignore)
  - `407e546` DESIGN.md v1.0 + Phase 2 tracking
- **Repository**: https://github.com/AlexOpasnost/trustgive (public)
- User authenticated via `gh auth login` (AlexOpasnost account, scopes: repo, workflow, gist, read:org)
- **Next**: User connects to Railway dashboard manually (PostgreSQL add-on first; GitHub deploy linkage deferred to Phase 3 when first backend code lands)

---

## [2026-05-05] [Project Lead] [Infra Setup — Railway]

- User created Railway project via dashboard, renamed to `trustgive`
- **Railway Project ID**: `09bd8e82-2325-4e13-8404-fe3f1832a0dd`
- PostgreSQL 17 service provisioned (DATABASE_URL ready for Phase 3 backend)
- Created skeleton `DEVOPS.md` (Phase 7 expansion deferred) with:
  - Current infra state (GitHub + Railway IDs)
  - CLI link instructions for future deploys
  - Frontend hosting plan (Cloudflare Pages vs Vercel decision deferred)
  - Phase 7 deliverables checklist
  - Cost projection through public launch
- Created `.env.example` with all required env vars (Django, DATABASE_URL, ProPublica/Every.org/CharityBase APIs, Sentry, PostHog) — placeholders only, no secrets
- **Files created/modified**: `DEVOPS.md`, `.env.example`, `PROJECTS.md` (root)
- **Next**: Awaiting Gate 2 approval of DESIGN.md → Phase 2.5 (Backend Developer for OpenAPI design + ADRs)

---

## [2026-05-05] [Project Lead] [Design Iteration — Hugeicons swap]

- User requested icon-library upgrade from Lucide → **Hugeicons Free**
- Verified that `garrytan/gstack` repo (referenced by user) does NOT contain Hugeicons or any specific UI template — it's a Claude Code agent framework analogous to our `app_creater`. Hugeicons is a separate library at hugeicons.com
- **Hugeicons Free** package: 5,100+ MIT icons, Stroke-Rounded style, `@hugeicons/react` + `@hugeicons/core-free-icons`
- Rationale: 4× larger catalogue than Lucide, more expressive editorial linework, still tree-shakeable, $0
- DESIGN.md updated to v1.1:
  - §4 Iconography: rewritten with Hugeicons rationale, install snippet, ~30-icon vocabulary mapped to likely Hugeicons names (Frontend Developer confirms exact names on import in Phase 4)
  - §11 Component library: added `@hugeicons/react` to stack
- README.md: added Hugeicons to stack list
- **Files modified**: `DESIGN.md`, `README.md`, `CHANGELOG.md`
- **Next**: Awaiting Gate 2 approval — DESIGN.md is now at v1.1 with Hugeicons
