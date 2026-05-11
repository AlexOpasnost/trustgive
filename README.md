# TrustGive

> The only charity discovery tool that shows you the source documents — not a star rating you can't audit.

**541 verified charities across 27 countries.** Every entry links to the original IRS Form 990, UK Charity Commission filing, CRA T3010, ACNC info statement, or the org's own audited annual report. **0% platform fee.** We never see your money — donations happen on the charity's own site.

🌐 **Live**: [trustgive.org](https://trustgive.org) · 🔧 **API**: [api.trustgive.org/api/docs](https://api.trustgive.org/api/docs)

---

## What's inside

| | |
|---|---|
| **Charities** | **541** (started May 5 with 11) |
| **Countries** | **27** (US/GB/RU + CA/AU/NZ + DE/NL/CH/SE/FR/IT/ES/IE/NO/BE/DK/PL/FI/AT + JP/SG/IN/TH/BR/CL/KE/IL) |
| **Regional filters** | 8 (All / Americas / Europe / Russia / Africa / MENA / Asia / Oceania) |
| **Buckets** | People (~370) · Planet (~95) · Animals (~75) |
| **Cause-tags** | ~110 (mental-health, climate, refugees, LGBTQ+, veterans, anti-trafficking, deafblind, rare-disease, etc.) |
| **Languages** | English + Russian; every visible string bilingual |
| **Hero photos** | ~340 with real og:image from the org's own site (rest fall back to BrandedAvatar gradient) |

---

## Why this exists

Existing charity-discovery tools fall into two camps:
1. **Rating aggregators** like Charity Navigator and GuideStar that publish opaque scores nonprofits learn to game (Charity Navigator dropped overhead-ratio scoring in 2023 for exactly this reason).
2. **Donation platforms** like JustGiving that bundle a default-on "tip" pulling 12.5–17.5% out of the gift before the charity sees a cent.

TrustGive is neither. It's a **discovery layer** built on free public data — IRS 990 filings, UK Charity Commission register, CRA T3010, ACNC info statements, national-regulator certifications (DZI Spendensiegel, CBF Erkend, ZEWO, 90-konto), and the org's own audited annual reports — that links you straight to the source. We don't process payments. We don't publish a single number you have to trust. We show the documents.

---

## Differentiator

> **One click reveals the source document.**

Click any charity → scroll to "Source documents" → see the actual Form 990 (US), Charity Commission accounts page (UK), T3010 information return (Canada), ACNC profile (Australia), Bilancio Sociale (Italy), or audited annual report (everywhere else). No paywall. No interpretation. The raw document.

For 339 US 501(c)(3)s the source is ProPublica's `/organizations/{ein}` overview page (not direct PDF — Cloudflare blocks bot HEAD requests on direct downloads). For 49 UK orgs it's the Charity Commission `/charity-search/-/charity-details/{number}/accounts-and-annual-returns` page. For everything else it's the org's own transparency/financials page.

---

## Stack

- **Backend**: Python 3.13 + Django 5.1 + DRF + drf-spectacular + Postgres (Neon serverless) on Railway
- **Frontend**: React 19 + TypeScript + Tailwind v4 + Vite — deployed as Cloudflare Worker
- **Search**: Postgres full-text search + pg_trgm trigram fuzzy matching
- **i18n**: i18next (English + Russian) · JSONB `{en, ru}` LocalizedTextField for every localised model field
- **CDN**: Cloudflare (api.trustgive.org proxied to Railway · s-maxage=120s · per-deploy cache purge)
- **Cache**: django-cachalot LocMem (per-gunicorn-worker) — invalidated on Railway redeploy
- **Images**: weserv.nl free CDN proxy for hero photos (~99% size reduction vs. direct hot-linking)
- **Logo backfill**: logo.uplead.com (apex-domain logos) with Google s2 favicons fallback for niche TLDs
- **OG-image scrape**: custom `manage.py scrape_og_images` command — fetches og:image / twitter:image / image_src from each charity's homepage, throttled 2s, Neon-reconnect-aware
- **Observability**: Sentry + python-json-logger + server-side PostHog mirror for donation_redirect events
- **Russia legal compliance**: defensive `is_blocked()` per-seed-entry check against war-relief / foreign-agent / extremist registries (Минюст-listed orgs auto-skipped)

---

## Status

✅ **v3.14 in production** as of 2026-05-11. Built from v0 to 541 charities in 7 days; +323 charities in the final day alone via 9 hand-written seed migrations.

| Phase | Status |
|---|---|
| 0 — Spec & intake | ✅ |
| 1 — Market research | ✅ |
| 2 — Design (v3 photo-first immersive) | ✅ |
| 3 — Backend (Django + DRF + Postgres) | ✅ |
| 4 — Frontend (React + TS + Tailwind) | ✅ |
| 5 — Live deployment (Railway + Cloudflare) | ✅ |
| 6 — Catalog scale (218 → 541) | ✅ |
| 7 — Mobile QA + Lighthouse audit | 🔄 Outstanding |

---

## Documentation

- [`SPEC.md`](SPEC.md) — v1.0 spec with user stories and Gherkin acceptance criteria
- [`MARKET_ANALYSIS.md`](MARKET_ANALYSIS.md) — competitor research (Charity Navigator, GiveWell, JustGiving), feature demand, anti-features
- [`DESIGN.md`](DESIGN.md) — v3.1 photo-first immersive design system
- [`API_SPEC.md`](API_SPEC.md) — OpenAPI 3.1 via drf-spectacular
- [`docs/adr/`](docs/adr/) — 8 Architecture Decision Records (database, auth, API style, deployment, etc.)
- [`CHANGELOG.md`](CHANGELOG.md) — every decision and migration logged in chronological order (~3500 lines)
- [`backend/apps/charities/blocklist.py`](backend/apps/charities/blocklist.py) — Russia-law compliance blocklist

---

## License

Source code: TBD. Catalog data: derived from public regulator filings; descriptions written by Project Lead.

---

Built solo by [Alex Diachenko](https://github.com/AlexOpasnost). Following along? Star the repo and follow on LinkedIn for build-in-public updates.
