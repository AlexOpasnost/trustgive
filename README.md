# TrustGive

> A discovery platform for verified charities. Built around one idea: instead of showing you a star rating somebody made up, link you straight to the regulator's filing.

[trustgive.org](https://trustgive.org) · [api docs](https://api.trustgive.org/api/docs) · [changelog](CHANGELOG.md)

**541 charities, 27 countries**, bilingual EN+RU. Started May 5, 2026 with 11 entries. As of v3.16 the catalog spans US, UK, Russia, Canada, Australia, New Zealand, most of continental Europe, Japan, India, Thailand, Brazil, Chile, Kenya, and Israel.

---

### Why this exists

I went to donate, got stuck on a basic question — *who do I trust to tell me which charities are real?* — and didn't like any of the answers I found.

The big aggregators (Charity Navigator, GuideStar) publish opaque scores that nonprofits learn to game. Charity Navigator quietly dropped its overhead-ratio metric in 2023 for exactly that reason. The donation platforms (JustGiving and similar) bundle 10–18 % "tips" on top of every gift before the charity ever sees it.

TrustGive doesn't grade anything. It links you to the regulator's file — Form 990 for US 501(c)(3)s, the Charity Commission's accounts page for UK charities, T3010 for Canada, ACNC info statement for Australia, Минюст СОНКО for Russia, audited annual reports for everyone else. If you want to donate, you click through and donate on the charity's own site. No platform fee, no account, no nudge.

### What's in there

| | |
|---|---|
| Charities  | **541** |
| Countries  | **27** |
| Buckets    | People `236` · Planet `64` · Animals `51` (verified tier) |
| Cause tags | ~110 — mental health, climate, refugees, LGBTQ+, veterans, anti-trafficking, rare disease, deafblind, etc. |
| Languages  | EN + RU end to end |
| Hero photos| ~340 real org photos, proxied through a Cloudflare Worker (more on this below) |

The Russian side of the catalog is curated. War-relief funds, foreign-agent-listed orgs, and extremist-listed orgs from the Минюст and Росфинмониторинг registries never get seeded — there's a defensive `is_blocked()` check in every seed migration so the rule is enforced at write time, not just by convention. See [`backend/apps/charities/blocklist.py`](backend/apps/charities/blocklist.py) if you want the list.

### The differentiator, in one sentence

One click to the source document. Most rating sites show you a score and bury the underlying filing several pages deep. TrustGive flips the order: a charity card lists what filings exist, and clicking one opens the actual document.

For 339 US orgs the source link goes to ProPublica's overview page for the EIN (not the direct 990 PDF — Cloudflare blocks bot HEAD requests on those downloads). UK charities link to the Charity Commission's accounts-and-annual-returns page. Everyone else links to whatever the national regulator publishes — or, where that doesn't exist publicly, the org's own audited annual report.

### Stack

Backend is Django 5.1 on Python 3.13, DRF for the API, drf-spectacular for the OpenAPI schema, Postgres on Neon serverless, deployed to Railway. Search is Postgres FTS + pg_trgm trigram fuzzy. Every translated field on every model is a JSONB `{en, ru}` `LocalizedTextField`.

Frontend is React 19 + TypeScript + Tailwind v4, built with Vite, deployed as a Cloudflare Worker that doubles as a static-asset host *and* runs the image proxy (more below). i18next handles language switching, TanStack Query handles all data fetching.

The image proxy is the part I'm most happy with. Wikimedia Commons is the most reliable source of free, licensed charity photos, but their thumbnail endpoint is locked behind a User-Agent policy that browsers can't satisfy. So `/img/v1` is a 150-line Cloudflare Worker that fetches Wikimedia thumbs with a compliant UA, snaps requested widths to their pre-cached tier (320/480/640/800/1024/1280/1600/2048), caches at the CF edge for 30 days, and sets the `Cross-Origin-Resource-Policy: cross-origin` header Chrome needs to render the image. Net effect: a Save the Children hero photo dropped from **3.5 MB to 67 KB** (98 % reduction). All the gory detail is in [`worker/index.ts`](worker/index.ts) and the v3.16 CHANGELOG entry.

Observability is Sentry + python-json-logger on the backend, with a server-side PostHog mirror for `donation_redirect` events so I can measure whether the discovery UI actually sends people somewhere.

### How fast this went

| Day | What |
|----|------|
| May 5  | 11 charities seeded. Deploy pipeline live. |
| May 8–10 | Catalog scale push. 218 → 471 in three days. |
| May 11 | v3.14 megabatch — single migration adding 70 charities + 4 new countries, hitting 541. Then mobile QA exposed three bugs no one had noticed (homepage bucket counts stale, `/charities` capped at 300 of 541, hero photos broken in Chrome). |
| May 12 | v3.15 fixed the three. v3.16 shipped the image-proxy Worker. |

The biggest surprise was how lopsided the work felt. The Django+React+CF infrastructure was maybe a day. The other six days were research — finding the right regulator URL for each org, copying the EIN/CC#/registration ID, writing two-sentence bilingual descriptions that don't sound like marketing copy, picking a press photo that's actually licensed. A five-line model schema is easy. Populating it honestly across 27 jurisdictions is not.

### Documentation

- [`SPEC.md`](SPEC.md) — user stories + Gherkin acceptance criteria from v0
- [`DESIGN.md`](DESIGN.md) — design system (v3 is the current photo-first immersive)
- [`MOBILE_QA.md`](MOBILE_QA.md) — Playwright + Lighthouse audit that surfaced the v3.15 bugs
- [`API_SPEC.md`](API_SPEC.md) — OpenAPI 3.1, generated from drf-spectacular
- [`docs/adr/`](docs/adr/) — eight Architecture Decision Records covering database, auth, API style, deployment
- [`CHANGELOG.md`](CHANGELOG.md) — chronological. Every decision, every migration, with retrospectives

### License

Code: TBD — leaning MIT, still figuring out the data-license question. Catalog data is derived from public regulator filings; descriptions and translations I wrote myself.

---

Built solo by [Alex Diachenko](https://github.com/AlexOpasnost) in Moscow.
