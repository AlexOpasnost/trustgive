# 05 — Deployment

## Production architecture

```
trustgive.org              → Cloudflare Pages (React SPA)
api.trustgive.org          → Railway (Django + Postgres)
admin.trustgive.org        → Railway (same Django, restricted IP allowlist) [planned]
```

## Backend (Railway)

### Initial deploy

Already provisioned per [`DEVOPS.md`](../DEVOPS.md):
- **Project name**: `trustgive`
- **Project ID**: `09bd8e82-2325-4e13-8404-fe3f1832a0dd`
- **PostgreSQL 17 service** already attached

To enable GitHub auto-deploy:

1. Open https://railway.app → `trustgive` project
2. Click **+ Create** → **GitHub Repo** → `AlexOpasnost/trustgive`
3. Set **Root directory**: leave blank (`railway.json` at repo root tells Railway to use `backend/Dockerfile`)
4. **Variables** → add:
   - `DJANGO_SECRET_KEY` — generate via `python -c "import secrets; print(secrets.token_urlsafe(50))"`
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=api.trustgive.org,trustgive.up.railway.app`
   - `DJANGO_CSRF_TRUSTED_ORIGINS=https://trustgive.org,https://api.trustgive.org`
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}` (reference)
   - `SENTRY_DSN=...` (from sentry.io project)
   - `SENTRY_ENVIRONMENT=production`
   - `POSTHOG_SERVER_KEY=phc_server_...`
   - `CF_API_TOKEN=...` (Cloudflare API token, Zone:Cache Purge scope)
   - `CF_ZONE_ID=...` (from Cloudflare dashboard for trustgive.org)
   - `APP_VERSION=1.0.0`
   - `EVERY_ORG_PUBLIC_KEY=...`
   - `EVERY_ORG_PRIVATE_KEY=...`
5. **Deploy** → first deploy runs `manage.py migrate` and `collectstatic` from the entrypoint script
6. Verify: `curl https://trustgive.up.railway.app/api/health/` → 200 OK

### Custom domain

In Railway: **Settings → Networking → Custom domain** → `api.trustgive.org`. Add the DNS records Railway shows (CNAME or A record) at Cloudflare DNS for trustgive.org.

### Healthcheck

Railway auto-restarts on 503. Configured in `railway.json`:
```json
{
  "deploy": {
    "healthcheckPath": "/api/health/",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

External uptime monitor: UptimeRobot (free, 50 monitors, 5-min interval) on `https://api.trustgive.org/api/health/`.

## Frontend (Cloudflare Pages)

### Initial deploy

1. Open https://dash.cloudflare.com → Workers & Pages → Create → Pages → **Connect to Git**
2. Authorize GitHub access; select `AlexOpasnost/trustgive`
3. **Build settings**:
   - Framework preset: `None`
   - Build command: `cd frontend/web && npm install && npm run build`
   - Build output directory: `frontend/web/dist`
   - Root directory (advanced): leave blank
   - Environment variables:
     - `VITE_API_BASE_URL=https://api.trustgive.org`
     - `VITE_POSTHOG_API_KEY=phc_public_...`
     - `VITE_POSTHOG_HOST=https://eu.i.posthog.com`
     - `VITE_SENTRY_DSN=...` (separate Sentry project from backend)
     - `NODE_VERSION=20`
4. Deploy. Cloudflare will give you a `*.pages.dev` URL.

### Custom domain

In Cloudflare Pages → **Custom domains** → add `trustgive.org`. Cloudflare auto-creates the CNAME (since DNS is at Cloudflare).

### Preview deploys

Every PR gets a unique `*.pages.dev` URL. Safe for QA — no production data.

## DNS plan

| Record | Type | Target |
|---|---|---|
| `trustgive.org` | A/AAAA | Cloudflare Pages (auto-managed) |
| `www.trustgive.org` | CNAME | `trustgive.org` (redirect via Page Rules) |
| `api.trustgive.org` | CNAME | Railway backend (custom domain) |
| `admin.trustgive.org` | CNAME | Railway backend [later, with IP allowlist] |

## Pre-launch checklist (Week 8)

Before public launch on Product Hunt + Show HN:

- [ ] All H-001 through H-003 from REVIEW_REPORT fixed (initial migration committed, ProPublica field mappings corrected, CORS configured)
- [ ] First successful nightly ETL run completed
- [ ] Catalog has ≥ 1,000 US charities + UK charities loaded
- [ ] 30 manually curated RU charities entered via admin
- [ ] Lighthouse on `/`, `/charities`, `/methodology` ≥ 90 Performance, ≥ 95 SEO+A11y
- [ ] k6 load test: 200 VUs against staging passes thresholds
- [ ] Sentry receiving events on test exception
- [ ] PostHog frontend + server-mirror events arriving
- [ ] UptimeRobot configured + Slack/email alerts
- [ ] Custom domains resolving + HTTPS valid
- [ ] CHANGELOG up to date
- [ ] Product Hunt assets ready (screenshots, demo video, hunter recruited)
- [ ] HN Show HN draft ready
