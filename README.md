# TrustGive

> The only charity discovery tool that shows you the source documents — not a star rating you can't audit.

Filter 1.2M+ verified US, UK, and Russian charities by cause, country, and size. Every "verified" claim links to the original IRS Form 990, UK Charity Commission filing, or Минюст registration. **0% platform fee.** We never see your money — donations happen on the charity's own site.

---

## Status

🚧 **In active development** — building in public. Soft-launch target: 8 weeks from kickoff.

| Phase | Status |
|---|---|
| 0 — Spec & intake | ✅ Done |
| 1 — Market research | ✅ Done — see [`MARKET_ANALYSIS.md`](MARKET_ANALYSIS.md) |
| 2 — Design | 🔄 In progress |
| 3 — Backend (Django + DRF + Postgres) | ⏳ Pending |
| 4 — Frontend (React + TS + Tailwind) | ⏳ Pending |
| 5 — Test / E2E / Perf / A11y | ⏳ Pending |
| 6 — Public launch (PH + HN) | ⏳ Pending |

---

## Why this exists

Existing charity-discovery tools fall into two camps:
1. **Rating aggregators** like Charity Navigator and GuideStar that publish opaque scores nonprofits learn to game (Charity Navigator dropped overhead-ratio scoring in 2023 for exactly this reason).
2. **Donation platforms** like JustGiving that bundle a default-on "tip" that pulls 12.5–17.5% out of the donor's gift before the charity sees a cent (JustGiving's #1 complaint on Trustpilot).

TrustGive is neither. It is a **discovery layer** built on free public data — IRS 990 filings, UK Charity Commission register, Минюст СОНКО registry — that links you straight to the source. We don't process payments. We don't publish a single number you have to trust. We show the documents.

---

## Stack

- **Backend**: Python 3.13 + Django 6 + DRF + PostgreSQL 17
- **Frontend**: React 19 + TypeScript + Tailwind v4 + Vite (web-first responsive)
- **i18n**: i18next (English + Russian at launch)
- **Data sources**: ProPublica Nonprofit Explorer API · Every.org Charity API · CharityBase.uk
- **Hosting**: Railway (backend + Postgres) + Cloudflare Pages or Vercel (frontend)
- **Observability**: Sentry · PostHog (cookie-less mode)

---

## Documentation

- [`SPEC.md`](SPEC.md) — full v1.0 spec with user stories and acceptance criteria
- [`MARKET_ANALYSIS.md`](MARKET_ANALYSIS.md) — competitor research, feature demand, anti-features, verification data sources
- [`DESIGN.md`](DESIGN.md) — UI/UX system (in progress)
- [`docs/adr/`](docs/adr/) — Architecture Decision Records (in progress)
- [`CHANGELOG.md`](CHANGELOG.md) — every decision logged in chronological order

---

## License

TBD before public launch.

---

Built solo by [Alex Diachenko](https://github.com/AlexOpasnost). Following along? Star the repo and follow on LinkedIn for build-in-public updates.
