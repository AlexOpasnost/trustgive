# DevOps — TrustGive

> **Status**: Infra skeleton (set up during Phase 2). Full deployment plan with 3 tier options (budget / mid / enterprise) will be produced by **DevOps Engineer agent** in **Phase 7**.

---

## Current Infrastructure (as of 2026-05-05)

### GitHub
- **Repository**: https://github.com/AlexOpasnost/trustgive
- **Visibility**: Public
- **Owner**: AlexOpasnost
- **Default branch**: `main`
- **CI/CD**: not yet configured (DevOps Engineer adds GitHub Actions in Phase 7)

### Railway
- **Project name**: `trustgive`
- **Project ID**: `09bd8e82-2325-4e13-8404-fe3f1832a0dd`
- **Environment**: `production` (default)
- **Region**: TBD (set by Railway based on first deploy)
- **Services**:
  - 🟢 **PostgreSQL 17** (Postgres add-on, provisioned 2026-05-05)
    - `DATABASE_URL` available in Variables
    - Used by: Django backend (will be linked in Phase 3)
  - ⏳ **Backend service** (Django) — pending Phase 3 code
  - ⏳ **Frontend service** OR external host (Vercel/Cloudflare Pages) — pending Phase 4 decision
- **Plan**: Hobby tier ($5/mo) on $5 trial credit; budget reserve ~$10–20/mo if traffic exceeds free Postgres

### CLI link (for future use)
Once code lands in `backend/`, link locally with:
```bash
cd projects/trustgive/backend
railway login                                 # one-time browser auth
railway link --project 09bd8e82-2325-4e13-8404-fe3f1832a0dd
railway up                                    # deploy current dir
```

Or rely on **GitHub auto-deploy** (recommended) — set up via Railway dashboard:
- Project page → **+ Create** → **GitHub Repo** → `AlexOpasnost/trustgive`
- Root directory: `backend/`
- Auto-deploy: every push to `main`
- Link `DATABASE_URL` env var from the Postgres service to the backend service (Variables → Reference → `${{Postgres.DATABASE_URL}}`)

---

## Frontend hosting (planned for Phase 4)

Two options to be evaluated by Frontend Developer + DevOps Engineer:

| Option | Pros | Cons | Cost |
|---|---|---|---|
| **Vercel** | Best Next.js DX; preview deploys per PR; built-in Image Optimization | Bandwidth limits in free tier; vendor lock-in | $0 hobby tier |
| **Cloudflare Pages** | Generous bandwidth; global edge; framework-agnostic | Less polished Next.js DX; some Next.js features missing | $0 free tier |
| **Railway (same project)** | One-place ops | Costs more; SSR worker not optimal | ~$5/mo |

**Default plan**: Cloudflare Pages for the frontend; Railway for backend + Postgres. Decision finalized in Phase 7.

---

## Observability (planned for Phase 3)

- **Sentry** (free tier ≤5K errors/mo) — backend exceptions + frontend JS errors
- **PostHog** (free tier 1M events/mo) — analytics, funnel, cookie-less mode
- **Logging**: structured JSON via `python-json-logger`, captured by Railway log drain
- **Health check**: `GET /api/health/` returning `{status, db, redis, sentry}` (200 OK or 503)

Backend Developer wires all of the above in Phase 3 per the `observability` skill.

---

## Secrets management

**Never commit**:
- `DATABASE_URL` (provisioned by Railway, referenced via `${{Postgres.DATABASE_URL}}`)
- `SECRET_KEY` (Django) — generated and set in Railway Variables
- `SENTRY_DSN` — from Sentry dashboard
- `POSTHOG_API_KEY` — from PostHog dashboard
- `EVERY_ORG_PRIVATE_KEY` — from Every.org developer console

`.env.example` in repo provides placeholders; real values live only in:
- Railway Variables (production)
- Local `.env` (gitignored)

Pre-commit hook: `gitleaks` (DevOps Engineer adds in Phase 7).

---

## Phase 7 deliverables (DevOps Engineer)

When Phase 7 runs, this file will be expanded with:

1. **3 tier options** (budget $0 / mid $20 / enterprise $200/mo) with concrete service mapping
2. **Dockerfile + docker-compose.yml** for local dev parity with production
3. **GitHub Actions workflow** (`.github/workflows/ci.yml`) — lint + test + deploy
4. **Pre-commit config** (ruff, ESLint, gitleaks)
5. **Makefile** (`make dev`, `make test`, `make migrate`, `make seed`)
6. **Backup strategy** for Postgres (Railway Backups add-on or pg_dump cron)
7. **Monitoring + alerting** setup (Sentry alerts, PostHog dashboards, Railway log alerts)
8. **Domain + SSL** plan (custom domain `trustgive.org` if Alex registers; Cloudflare DNS)
9. **Rollback procedure** (Railway redeploy from previous commit; database migration safety)
10. **Runbook** for common ops tasks (rotate secrets, restore DB, scale dyno, update charity dataset)

---

## Cost projection

| Phase | Stage | Monthly cost |
|---|---|---|
| W1–W6 | Build, alpha, beta — single dev | $0 (trial credit) |
| W7 | Soft launch — ~50 visitors/day | $0–$5 |
| W8 | Public launch — PH spike, 5K visitors | $5–$15 |
| Post-launch steady state | 5K/mo visitors | $5–$10 |
| If traction (50K/mo by month 4) | Scale Postgres + add CDN | $20–$40 |

All within the SPEC §10 ceiling of "$10–20/mo if traffic exceeds free tiers".
