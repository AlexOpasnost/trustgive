# DevOps — TrustGive

> **Status**: Phase 7 deliverable (full)
> **Date**: 2026-05-05
> **Author**: Project Lead (DevOps Engineer agent skipped per sandbox lessons)

---

## 1. Current infrastructure (provisioned)

### GitHub
- **Repository**: https://github.com/AlexOpasnost/trustgive (public)
- **Owner**: AlexOpasnost
- **Default branch**: `main`
- **CI/CD**: GitHub Actions workflows in `.github/workflows/`

### Railway
- **Project name**: `trustgive`
- **Project ID**: `09bd8e82-2325-4e13-8404-fe3f1832a0dd`
- **Environment**: `production` (default)
- **Services**:
  - 🟢 **PostgreSQL 17** — provisioned 2026-05-05; `DATABASE_URL` available in service variables
  - ⏳ **Backend service** — pending GitHub-Repo link via Railway dashboard
  - 🌐 **Frontend** — Cloudflare Pages (planned, separate from Railway)

---

## 2. Three deployment tier options

### 🟢 Budget tier ($0–$10/month) — MVP launch

The current setup. Use until traction is real.

| Service | Provider | Cost |
|---|---|---|
| Backend (Django + gunicorn) | Railway hobby | $5/mo + free trial credit |
| Postgres 17 | Railway add-on | included in hobby |
| Frontend SPA | Cloudflare Pages | Free (unlimited requests) |
| CDN | Cloudflare proxy in front of api.trustgive.org | Free |
| Error tracking | Sentry | Free (5K errors/mo) |
| Analytics | PostHog Cloud EU | Free (1M events/mo) |
| Uptime | UptimeRobot | Free (50 monitors) |
| Email | None (no email infra in MVP) | $0 |
| **Total** | | **~$5/mo** after trial credit |

**Capacity**: 5K monthly visitors, 200 concurrent users peak. Sufficient for SPEC §9 targets and the Week 8 Product Hunt launch spike.

**Limitations**:
- 1 GB Postgres storage on lowest tier — supports ~150K charity records before upgrade needed
- 1–3 worker processes = per-worker cachalot LocMem (acceptable, see ADR-007)
- No staging environment

---

### 🟡 Mid tier ($20–$40/month) — post-launch growth

When monthly visitors cross 25K or charity dataset exceeds 200K rows.

| Service | Provider | Cost |
|---|---|---|
| Backend | Railway Pro | $20/mo |
| Postgres Pro (10GB) | Railway add-on | $5/mo |
| Redis cache | Railway Redis | $5/mo |
| Frontend | Cloudflare Pages Pro | $20/mo (analytics + faster build) |
| Sentry | Team tier | $26/mo (50K events/mo) |
| PostHog | Pay-as-you-go | ~$0–10/mo at this scale |
| **Total** | | **~$80/mo** |

**Triggers to upgrade**:
- Cachalot per-worker miss rate > 50% in PostHog → flip to Redis
- Postgres approaching 1GB ceiling
- Sentry free tier exceeded (>5K errors/mo — likely after 25K visitors)
- Need PR preview deploys with branch protection

**What changes**:
- `CACHES['default']['BACKEND'] = 'django.core.cache.backends.redis.RedisCache'` — DRF throttle becomes globally consistent
- Cachalot uses Redis automatically (no code change)
- Lighthouse perf budget more comfortable — Cloudflare Pro caches more aggressively

---

### 🔴 Enterprise tier ($200+/month) — if/when commercialised

Only relevant if TrustGive ever moves beyond a portfolio piece. Documented for completeness.

| Service | Provider | Cost |
|---|---|---|
| Backend | AWS ECS Fargate (3 containers) | $50–80/mo |
| Postgres | AWS RDS (db.t4g.medium, multi-AZ) | $80/mo |
| Redis | AWS ElastiCache | $20/mo |
| Frontend | Cloudflare Pages or Vercel Pro | $20/mo |
| Search | Self-hosted Meilisearch on Fly.io | $5/mo |
| Sentry | Business tier | $80/mo (200K events) |
| PostHog | Self-hosted on Fly.io | $20/mo |
| Datadog or BetterStack | logs + APM | $40/mo |
| Email (transactional) | Postmark | $15/mo |
| **Total** | | **~$330/mo** |

**Triggers**:
- 250K+ monthly visitors
- Multi-region requirement
- SLA commitments to partners
- Compliance audit requirements (SOC 2, etc.)

**Architecture changes**:
- Multi-region Postgres replicas
- Active-active deploy (blue/green)
- Dedicated APM (Datadog) replacing free Sentry tier
- Self-hosted PostHog for data sovereignty
- Migration from Postgres FTS to Meilisearch (per ADR-005 cutover threshold)

---

## 3. CI/CD — GitHub Actions

Workflows in `.github/workflows/`:

| Workflow | Trigger | What it runs |
|---|---|---|
| `ci.yml` | Every PR + push to main | Lint + typecheck + test |
| `deploy.yml` | Push to main only | Deploy backend (Railway) — though Railway also auto-deploys |
| `e2e.yml` | PR labeled `e2e` | Playwright E2E suite against preview deploy |
| `perf.yml` | Weekly cron + manual dispatch | k6 load test + Lighthouse CI |
| `etl.yml` | Daily cron 02:00 UTC | `railway run python manage.py ingest_propublica --since=24h` |

See [`.github/workflows/`](.github/workflows/) for actual YAML.

## 4. Pre-commit hooks

`.pre-commit-config.yaml` at project root runs locally before each commit:
- `ruff check` + `ruff format` (Python)
- ESLint + Prettier (TypeScript)
- `gitleaks` (scan for accidentally committed secrets)
- `check-yaml`, `end-of-file-fixer`, `trailing-whitespace` (basic hygiene)

Install with:
```bash
pip install pre-commit
pre-commit install
```

## 5. Makefile (developer ergonomics)

`Makefile` at project root provides cross-platform commands:
```bash
make dev        # docker-compose up (postgres) + backend runserver + frontend npm run dev
make test       # backend pytest + frontend vitest
make lint       # ruff + eslint
make migrate    # python manage.py migrate
make seed       # ingest_propublica --bootstrap --limit=100
make perf       # k6 run
```

## 6. Observability stack (deployed)

Per ADR-008:
- **Sentry**: backend + frontend exception capture, free tier
- **PostHog**: frontend client + server-side mirror for donation_redirect (adblock-resistant)
- **Logging**: structured JSON via `python-json-logger`, Railway log viewer; future log drain to BetterStack ($0 free tier)
- **Health check**: `GET /api/health/` returns 200/503 — UptimeRobot polls 5-min, Railway polls 30s
- **Metrics**: Railway built-in dashboard (CPU, memory, RPS, latency); Sentry release-health tracks deploy stability

## 7. Backup + disaster recovery

- **Postgres backups**: Railway nightly automatic, 7-day retention on hobby tier
- **Manual backup**: `railway run pg_dump $DATABASE_URL > trustgive-$(date +%Y%m%d).sql`
- **Restore drill**: documented in [`DOCS/06-operations.md`](DOCS/06-operations.md) — should be tested before public launch
- **GitHub repo**: itself a backup of all spec/code/docs; cloned at multiple devs locally

## 8. Domain + SSL plan

- `trustgive.org` registered (TODO: Alex registers via Cloudflare Registrar — $9/yr or wait for first donor revenue to subsidise)
- DNS at Cloudflare → auto-provisioned Universal SSL
- Subdomains:
  - `trustgive.org` — Cloudflare Pages (frontend)
  - `api.trustgive.org` — Railway backend custom domain
  - `admin.trustgive.org` — Railway backend, IP allowlist (planned)

Until domain is registered, the site lives at:
- `<random>.pages.dev` (Cloudflare Pages auto-domain)
- `<random>.up.railway.app` (Railway auto-domain)

Both work for MVP soft-launch.

## 9. Submission checklist

Not applicable for web-first MVP. Once mobile (Phase 4.5+ optional):
- App Store Connect (Apple Developer $99/yr) — out of scope
- Google Play Console ($25 one-time) — out of scope

## 10. Cost projection through public launch

| Phase | Stage | Monthly burn |
|---|---|---|
| W1–W6 | Build, alpha, beta — single dev | $0 (Railway trial credit) |
| W7 | Soft launch — ~50 visitors/day | $0–5 |
| W8 | Public launch (PH/HN spike) — 5K visitors burst | $5–15 |
| Post-launch | 5K monthly steady state | $5–10 |
| Month 4 | 50K monthly (SEO long-tail) | $20–40 (mid tier kicks in) |
| Month 6 | 100K monthly | $40–80 |

**Total spend through Week 8 launch**: estimated **$5–25** (well within $200 project budget).

## 11. Pre-launch DevOps gate (Week 7-8)

- [ ] All 3 H-* findings from REVIEW_REPORT fixed
- [ ] First successful nightly ETL run
- [ ] CI/CD green on main (lint + test pass; deploy succeeds)
- [ ] Railway custom domain `api.trustgive.org` resolving
- [ ] Cloudflare Pages custom domain `trustgive.org` resolving
- [ ] HTTPS valid on both
- [ ] `pre-commit install` documented in DOCS/04-setup.md
- [ ] Sentry receiving real events (test with deliberate exception)
- [ ] PostHog receiving frontend pageviews + server-mirror events
- [ ] UptimeRobot configured + alert delivery tested
- [ ] Backup restore drill executed once
- [ ] Cost tracking up-to-date in `costs/COSTS.md`

## 12. Open items (Phase 4.5+)

- Pre-commit `gitleaks` config refinement (regex for known false-positives)
- BetterStack log drain — needs Railway → BetterStack drain config
- Self-hosted PostHog if EU privacy concerns escalate
- Multi-region Postgres replica (mid tier upgrade)
- CDN cache hit rate dashboard (Cloudflare Analytics + custom Grafana)
