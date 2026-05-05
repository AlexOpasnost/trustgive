# Project Specification: TrustGive

> **Status**: ✅ Approved v1.0
> **Created**: 2026-05-05 · **Approved**: 2026-05-05
> **Approval covers**: Gate 0 (Intake) + Gate 1 (Market Research) — combined approval after Phase 1
> **Repository**: https://github.com/AlexOpasnost/trustgive

---

## 1. Problem & Solution

**Problem Statement**:
People worldwide want to donate to charity but struggle to find organizations they can trust. They don't know which charities are legitimate, where the money actually goes, or how to filter charities by cause, geography, or efficiency. Existing services either game opaque rating systems (Charity Navigator), lock data behind paywalls (GuideStar), or bundle donations with hidden "tips" (JustGiving's #1 Trustpilot complaint).

**Proposed Solution**:
TrustGive is a **discovery platform** (not a payment processor) that helps users find verified charity organizations through powerful filters and **direct links to source documents** (IRS Form 990, UK Charity Commission filings, Минюст registrations). We aggregate publicly verifiable trust signals and expose them clearly. Users discover a charity here, then donate directly on the charity's own site — TrustGive **never handles money**.

**Positioning Statement** (homepage hero):
> The only charity discovery tool that shows you the source documents — not a star rating you can't audit.
> Filter 1.2M+ verified US, UK, and Russian charities by cause, country, and size.
> Every "verified" claim links to the actual IRS 990 / Charity Commission / Минюст document.
> 0% platform fee. We never see your money.

**Success Criteria**:
- A user can find 3 trustworthy charities matching their preferences in **under 90 seconds** from landing
- For each charity, the user can see WHY it is verified (source documents linked, one click)
- Net Promoter Score ≥ 40 from first 100 users
- Portfolio metric: featured on Product Hunt, shared in 2+ niche communities (r/EA, EA Forum, Indie Hackers)
- 50K monthly organic visits by month 4 (auto-generated SEO pages)

---

## 2. Target Users

**Primary User**:
A globally distributed donor (English-speaking primary, Russian-speaking secondary), held back from donating by lack of trust in charity organizations. May be a first-time donor exploring options or an experienced donor frustrated by opaque platforms. Income range $30K–$150K/year, motivated by personal cause (animals, children, climate, education) or recent news event.

**Secondary Users**:
- Russian-speaking donors abroad (under-served by US/UK platforms; under-served by RU platforms in English)
- Researchers, journalists checking charity legitimacy (use the source-document features)
- Effective Altruism community members evaluating non-EA causes with rigor

---

## 3. Core Features (MVP) — MoSCoW Prioritization

### Must Have (ship Week 8 with all of these)

| # | Feature | Description |
|---|---|---|
| 1 | **Charity catalog with multi-facet filters** | Filter by cause × country × size × verification status |
| 2 | **Source-document transparency** | Each charity profile links directly to its IRS 990 / Charity Commission filing / Минюст registration. One-click reveal. **TrustGive's primary wedge.** |
| 3 | **"Where the money goes" breakdown** | Top 5 expense lines from Form 990 (program / admin / fundraising / executive comp) with chart |
| 4 | **Trust badge aggregation** | Show external badges where present (BBB Accredited, Charity Commission registration, Минюст СОНКО status) |
| 5 | **Direct outbound "Donate" button** | Routes to charity's own donation page; clear "0% platform fee — we never touch your money" label |
| 6 | **English + Russian UI** | i18n via i18next; both languages at launch |
| 7 | **"How we verify" methodology page** | One-page explanation of TrustGive verification standard + what we do NOT verify |
| 8 | **Auto-generated SEO charity pages** | Per-charity SSR page targeting `"is [charity] legitimate"`, `"[charity] form 990"` long-tails |
| 9 | **Anonymous browsing (no login)** | All catalog/search/detail accessible without account |
| 10 | **Press mentions per charity (curated)** | `news_mentions[]` field — links to news articles citing the charity (substitutes for risky user-review system) |

### Should Have

| # | Feature | Description |
|---|---|---|
| 11 | **RSS feed of newly added charities** | 30-min build replaces email digest; serves the 5% who want updates without GDPR/email compliance overhead |
| 12 | **Compare 2–3 charities side-by-side** | Filter results → checkbox compare action |
| 13 | **OpenGraph cards for sharing** | Each charity page has shareable preview image |
| 14 | **PostHog analytics (privacy-respecting)** | Cookie-less event tracking; for portfolio "X visitors" metric |

### Could Have

| # | Feature | Description |
|---|---|---|
| 15 | **Saved-search via shareable URL** | `?cause=animals&country=US&size=small` URL works as bookmark |
| 16 | **Methodology blog** | Long-form posts ("Reading IRS 990 in 5 min", "Why we don't show overhead ratios") — fuels SEO |

### Won't Have (v1)

- ❌ User accounts / login / favorites — defer to v2 (no clear demand; JustGiving complaints flag forced sign-up)
- ❌ AI recommender — liability risk; "show source documents" is the better wow factor
- ❌ Email digest — replaced by RSS
- ❌ User reviews / star ratings — review-bombing risk + defamation liability
- ❌ Mobile native app — responsive web is sufficient at MVP
- ❌ Charity self-onboarding portal — Alex curates manually for v1
- ❌ Languages beyond EN+RU
- ❌ **Payment processing — forever** (this is core positioning, not a deferral)

---

## 4. Core User Stories (Gherkin acceptance criteria)

### Story 1: First-time donor finds a verified charity by cause

**As a** first-time donor concerned about animal welfare
**I want** to find verified animal-welfare charities in my country
**So that** I can donate to a legitimate organization without falling for a scam

**Acceptance Criteria**:
```gherkin
Given I am on the TrustGive homepage
When I select "Animals" from the cause filter and "United States" from the country filter
Then I see a list of at least 10 verified US animal-welfare charities
And each result shows: name, trust badges, % to programs, "Verified by [registry]" label
And I can click any result to view its detail page
```

### Story 2: Skeptical donor verifies the source documents

**As an** experienced donor who doesn't trust star ratings
**I want** to see the original government filing for a charity
**So that** I can verify the trust claim myself

**Acceptance Criteria**:
```gherkin
Given I am on a charity detail page
When I click "View source documents"
Then I see a list including: IRS Form 990 (most recent year), Charity Commission filing, or Минюст registration
And each link opens the original PDF / official registry page in a new tab
And the page clearly states the date of the most recent filing
```

### Story 3: Bilingual donor uses Russian UI

**As a** Russian-speaking donor in Berlin
**I want** to browse charities in Russian
**So that** I can confidently evaluate organizations in my native language

**Acceptance Criteria**:
```gherkin
Given I am on the TrustGive homepage with English UI
When I switch the language toggle to "Русский"
Then all UI labels, navigation, filter names, and methodology text appear in Russian
And the URL updates to /ru/...
And my language preference persists across sessions (localStorage, no account)
```

### Story 4: Donor clicks through to charity's own site

**As a** donor who has selected a charity to support
**I want** to donate directly on the charity's site
**So that** TrustGive doesn't take a cut and I retain full donor relationship with the charity

**Acceptance Criteria**:
```gherkin
Given I am on a charity detail page
When I click the primary "Donate" button
Then a modal informs me: "You're leaving TrustGive. We charge 0% — your full donation goes to [charity]"
And clicking "Continue" opens the charity's own donation page in a new tab
And the event is logged to PostHog as `donation_redirect`
```

### Story 5: SEO landing — "is X legitimate" search

**As a** donor who Googled "is [charity name] legitimate"
**I want** to land on a clear page that answers the question with evidence
**So that** I can decide whether to give without further research

**Acceptance Criteria**:
```gherkin
Given a charity has been ingested from ProPublica or CharityBase
When Google indexes the auto-generated SEO page
Then the page H1 is "Is [charity name] a legitimate charity?"
And the page leads with verification status + source-document links
And meta description includes the charity's EIN/registration number
And the page passes Lighthouse SEO score ≥ 95
```

### Story 6: Comparing 2 charities

**As a** donor deciding between two animal-welfare charities
**I want** to compare their financials side-by-side
**So that** I can choose the better-run one

**Acceptance Criteria**:
```gherkin
Given I have used a filter to view a results list
When I select the "Compare" checkbox on 2 charities and click "Compare"
Then I see a side-by-side table: trust badges, total revenue, % to programs, % admin, % fundraising, executive comp, last filing date
And I can click "Donate" directly from either column
```

---

## 5. Platforms

- [x] **Web (responsive React app)** — works on desktop + mobile browser
- [ ] Android (deferred to post-MVP)
- [ ] iOS (deferred to post-MVP)

**Minimum supported browsers**: last 2 versions of Chrome, Safari, Firefox, Edge

**Rendering strategy**: SSR/SSG required for SEO (per-charity pages must be crawlable). Stack TBD by Frontend Developer (Next.js OR Django+HTMX with Vite-built React islands).

---

## 6. Technical Requirements (finalized)

| Requirement | Decision |
|---|---|
| **User Accounts** | ❌ None in MVP. Anonymous browse + i18n preference in localStorage |
| **Authentication** | N/A in MVP |
| **Payments** | ❌ Never. TrustGive is a discovery layer. No PCI scope, no payment integration |
| **Push Notifications** | ❌ None |
| **Real-time Features** | ❌ None |
| **Search engine** | Postgres full-text search (free); upgrade to Meilisearch if needed in v2 |

### Required Integrations (final list)

| Integration | Purpose | Cost | Notes |
|---|---|---|---|
| **ProPublica Nonprofit Explorer API v2** | US charity data, IRS 990 | FREE, no key | Attribution required; ETL once + nightly delta |
| **Every.org Charity API** | Cause taxonomy + charity logos/descriptions | FREE non-commercial | Sign-up required; pair with ProPublica |
| **CharityBase.uk** | UK charity data | FREE, no key | Bulk JSON download + GraphQL |
| **Минэкономразвития реестр СОНКО** | RU verification (manual ingestion) | FREE | Manual curation of 30 charities for v1 |
| **PostHog** | Analytics, funnel tracking | FREE tier | Cookie-less mode for GDPR |
| **Sentry** | Error tracking | FREE tier (≤5K errors/mo) | |
| **i18next** | EN+RU localization | FREE | Frontend lib |

### Data Schema (high level — to be detailed in BACKEND.md)

- **Charity**: name, slug, EIN/registration_id, country, cause_tags[], description, logo_url, donation_url, last_filed_date, verification_status, source_documents[], trust_badges[], news_mentions[]
- **Financial**: charity_id, year, total_revenue, program_expenses, admin_expenses, fundraising_expenses, executive_comp_top, source_url
- **Cause**: slug, name_en, name_ru, parent_cause_id (taxonomy from Every.org)
- **Source document**: charity_id, kind (irs_990 / charity_commission / minjust / audit), url, filed_date, source

---

## 7. Design Preferences

**Visual Style**: Clean, trustworthy, slightly editorial. Conveys credibility without feeling corporate-cold. References to be researched in Phase 2: *Stripe Press*, *The New York Times Open*, *Charity:Water* (their "100% model" + GPS-tagged photos UX), *Effektiv-Spenden* (typography-led trust UI), *Linear* (modern minimalism).

**Must-show on every charity page**: trust badges, source-document links, "0% platform fee" label, "Donate on charity's own site" outbound CTA.

**Existing Brand**: None — Designer agent creates from scratch in Phase 2.

---

## 8. Market Context (from Phase 1)

**12 competitors analyzed** (full report: `MARKET_ANALYSIS.md`). Most direct conceptual rivals:
- **Charity Navigator** (US) — gameable scoring, dropped overhead ratios in 2023; Encompass methodology opaque
- **Effektiv-Spenden** (DE) — strong methodology rigor but only ~20 curated charities
- **VK Добро / Благо.ру** (RU) — strong vetting, walled garden, Russia-only, no English

**Key Differentiators**:
1. **Source-document transparency** (primary wedge) — one-click reveal of IRS 990 / Charity Commission filing
2. **Bilingual EN+RU coverage** — no platform shows RU charities to EN-speaking donors with verification proof
3. **0% platform fee + no money handling** — direct anti-pitch to JustGiving's hidden-tip complaints

---

## 9. Constraints & Non-Functional Requirements

| Requirement | Target |
|---|---|
| **Time to interactive** | < 2.5s on 4G mobile |
| **Search/filter response** | < 300ms server-side |
| **Lighthouse Performance** | ≥ 90 |
| **Lighthouse SEO** | ≥ 95 |
| **Accessibility** | WCAG 2.1 AA (audited Phase 4.5) |
| **Concurrency target (v1)** | 200 concurrent users peak; 5,000 monthly visitors |
| **Scaling ceiling without re-architecture** | 50K monthly visitors |
| **Compliance** | GDPR-friendly; minimal personal data; no payment data → no PCI |
| **Browser support** | Last 2 versions Chrome / Safari / Firefox / Edge |

---

## 10. Timeline & Budget

**Project Type**: Personal / Portfolio (US business school applications — social-impact angle)

**Timeline**: **8-week MVP** (Phase 1 already complete = Week 0)

| Week | Milestone |
|------|-----------|
| W1 | Setup: Django + Postgres + React skeleton; Railway free tier; ProPublica spike + 1K US charity ETL |
| W2 | **Internal alpha**: catalog + filter + detail page + 990 link + "How we verify" stub |
| W3 | UK ingestion (CharityBase); trust-badge aggregator; "where money goes" component |
| W4 | **Closed beta**: 30 RU manual curation; EN+RU i18n; PostHog wired; share with 10 testers |
| W5 | SEO foundation: SSR; per-charity pages; sitemap; OpenGraph |
| W6 | Hardening: Lighthouse 90+; WCAG 2.1 AA pass; 3 long-form blog posts; demo video |
| W7 | **Soft launch** on Indie Hackers + LinkedIn; gather 50–100 visitors; fix top 3 frictions |
| W8 | **Public launch** (PH + Show HN, Wednesday 12:01 AM PT) + Reddit/EA Forum follow-up |

**Hosting Budget**: **$0/month**
- Railway free tier (Postgres + Django web + worker)
- Cloudflare Pages or Vercel free tier (frontend)
- PostHog free tier (1M events/mo)
- Sentry free tier (5K errors/mo)
- Scaling reserve: ~$10–20/mo if traffic exceeds free tiers

---

## 11. Promotion Strategy (summary — full plan in MARKET_ANALYSIS.md §6)

**Launch channels** (priority): Product Hunt → Show HN → r/EffectiveAltruism + EA Forum → Indie Hackers → LinkedIn build-in-public

**SEO bet**: auto-generated per-charity pages targeting `"is [charity] legitimate"` long-tails. 1,000 charities × 50 visits/mo = 50K monthly organic by month 4.

**Partnerships (free)**: EA Hub linkbacks, Russian-speaking expat communities, university philanthropy syllabi, opportunistic disaster-response Reddit threads.

---

## Approval

- [x] User has reviewed and approved this specification (Gate 0 + Gate 1 combined approval)
- [x] All open questions resolved (was 7 open in v0.1; all closed in v1.0)
- [x] Team has confirmed feasibility of all Must Have features (Market Analyst confirmed free APIs for all data sources)

**Approved by user**: 2026-05-05 ("продолжаем")
