# 06 — Operations runbook

Common ops tasks. Each section is self-contained — search by symptom or task.

---

## Daily / weekly tasks

### Review flagged duplicates from ETL
**When**: weekly, Monday morning
**Why**: ETL flags charity name matches between 0.85 and 0.92 trigram similarity for human review (per ADR-004 tiered dedup)

```bash
# Connect to admin
https://admin.trustgive.org/admin/  # staff login required

# Or via shell
railway run python manage.py shell
>>> from apps.ingestion.models import IngestionLog
>>> recent = IngestionLog.objects.filter(status="partial").order_by("-started_at")[:10]
>>> for log in recent:
...     print(log.errors)  # check for "flagged" entries
```

If a flagged match is correct, manually merge via admin. If wrong, no action needed (the new charity was created).

### Check ingestion job health
**When**: every morning
**Where**: GitHub Actions cron logs + Railway → Logs → search `IngestionLog`

Healthy log line example:
```json
{"level":"INFO","message":"Done: status=succeeded seen=4823 upserted=312 skipped=4511 errors=0","request_id":""}
```

If you see `status=failed` or `errors > 0` repeatedly: investigate. Most common cause = ProPublica API schema change.

---

## Deploy

### Backend (auto on push to main)

```bash
git push origin main
# Railway auto-detects, builds Dockerfile, runs migrate + collectstatic, starts gunicorn
# Watch logs: railway logs --follow
```

### Frontend (auto on push to main)

Cloudflare Pages auto-builds on push. ~2 minutes from commit to deployed.

### Manual rollback

```bash
# Backend — Railway dashboard → Deployments → click previous → "Redeploy"
# OR via CLI:
railway redeploy --deployment <deployment-id>

# Frontend — Cloudflare Pages → Deployments → click previous → "Rollback to this deployment"
```

---

## Secrets rotation

### Django SECRET_KEY
**When**: yearly, or immediately if leaked

```bash
# Generate new key
NEW_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")

# Update in Railway Variables
railway variables set DJANGO_SECRET_KEY="$NEW_KEY"

# Redeploy
railway up
```

Note: rotating SECRET_KEY invalidates all admin sessions — staff must re-login. Acceptable since no public users have sessions (no auth in MVP per ADR-002).

### Sentry DSN
1. Sentry → Project Settings → Client Keys → revoke old, create new
2. Railway Variables → update `SENTRY_DSN`
3. Redeploy

### Cloudflare API token
1. Cloudflare → My Profile → API Tokens → revoke old, create new with `Zone:Cache Purge` scope
2. Railway Variables → update `CF_API_TOKEN`
3. Redeploy

### PostHog server key
1. PostHog → Project Settings → Project API Keys → rotate
2. Railway Variables → update `POSTHOG_SERVER_KEY`
3. Redeploy

---

## Database

### Backup
Railway provides automatic daily backups (Postgres add-on) — recover via Railway dashboard. Manual backup:

```bash
railway run pg_dump $DATABASE_URL > trustgive-$(date +%Y%m%d).sql
```

### Restore from backup

```bash
# Restore to local
psql -h localhost -U postgres trustgive < trustgive-20260505.sql

# Restore to Railway (rare; usually use Railway's UI)
railway run psql $DATABASE_URL < trustgive-20260505.sql
```

### Recompute search vectors
**When**: after a bulk schema change to `Charity.name` or `Charity.description`

```bash
railway run python manage.py shell -c "
from apps.charities.models import Charity
from django.db import connection
# Force trigger to fire on every row by touching name with no-op update
with connection.cursor() as cur:
    cur.execute('UPDATE charities_charity SET name = name')
"
```

### Reindex GIN indexes
**When**: after a `pg_trgm` version upgrade or perceived search performance drop

```bash
railway run psql $DATABASE_URL -c "REINDEX INDEX CONCURRENTLY charity_search_gin;"
railway run psql $DATABASE_URL -c "REINDEX INDEX CONCURRENTLY charity_name_trgm_idx;"
```

---

## Cache management

### Manual Cloudflare cache purge

If a charity update needs to invalidate immediately (faster than the Charity.post_save signal debounce):

```bash
# Purge specific URLs
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"files":["https://api.trustgive.org/api/charities/givedirectly/"]}'

# Or purge everything (rate-limited to 1/day on free plan)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"purge_everything":true}'
```

### Disable cachalot in production (debugging)

```bash
railway variables set CACHALOT_ENABLED=False
railway redeploy
# Don't forget to flip back when done
```

---

## ETL operations

### Replay a failed ingestion

```bash
railway run python manage.py shell -c "
from apps.ingestion.models import IngestionLog
log = IngestionLog.objects.get(id='<uuid>')
print(log.raw_payload)  # inspect
# Re-process: re-run the original command, raw_data_hash short-circuit will skip identical records
"

railway run python manage.py ingest_propublica --since=24h
```

### Force reprocess a specific charity

```bash
railway run python manage.py shell -c "
from apps.ingestion.models import SourceMapping
SourceMapping.objects.filter(source='propublica', source_id='271661997').update(raw_data_hash=b'')
# Next ingestion run will re-process this record (hash mismatch = no short-circuit)
"

railway run python manage.py ingest_propublica --ein=271661997
```

### Manually add a Russian charity

Via admin (https://admin.trustgive.org/admin/charities/charity/add/):
- Slug: lowercase-hyphenated (e.g. `nuzhna-pomosch`)
- Country: RU
- Registration ID: ОГРН number
- Name (LocalizedTextField): `{"en": "Nuzhna Pomosch", "ru": "Нужна помощь"}`
- Ingestion source: `manual_ru`
- Verification status: typically `verified` (you've checked Минюст)
- Donation URL: charity's own donate page
- Save

Then add Financial + SourceDocument inline records pointing to Минюст registration page.

---

## Monitoring + alerts

### Where to look

| Concern | Tool |
|---|---|
| Backend errors | Sentry → trustgive backend project |
| Frontend errors | Sentry → trustgive frontend project |
| User funnel + analytics | PostHog dashboard |
| Server health | Railway → trustgive → Logs / Metrics |
| Uptime | UptimeRobot dashboard |
| DNS / cache | Cloudflare → trustgive.org → Analytics |

### Alert configuration

- **Sentry**: email on any new error grouping (default for free tier)
- **Railway**: email on deploy failure / healthcheck restart
- **UptimeRobot**: email + SMS on `/api/health/` returning non-200 for >5 min
- **Cloudflare**: alert on Origin 5xx > 1% for 10 min (Settings → Notifications)

---

## Common incidents

### "Site is down"
1. Check `https://api.trustgive.org/api/health/` → if 503, DB or critical dep down
2. Check Railway logs for the last error
3. Check Sentry for the recent exception group
4. If DB issue: Railway Postgres dashboard → Connection check
5. Rollback if it's deploy-correlated

### "All catalog requests return 500 after my deploy"
- Likely cause: schema migration didn't run (Dockerfile entrypoint should handle this; verify in Railway logs)
- Quick fix: `railway run python manage.py migrate`

### "ProPublica ETL keeps failing"
- Check ProPublica's status page
- Check rate limit: are we under 5 req/sec? Look at `ThrottledHTTPClient` logs
- ProPublica might have changed their schema — open a Github issue, manually patch `_process_record` in `ingest_propublica.py`

### "Frontend shows the design but no data"
- Backend reachable? `curl https://api.trustgive.org/api/health/`
- CORS error in browser console? See REVIEW_REPORT H-003 — `django-cors-headers` not yet wired

### "Cache won't invalidate after I updated a charity"
- 60s debounce on `Charity.post_save` signal (per `apps/charities/signals.py:_DEBOUNCE_SECONDS`)
- Manual purge if urgent (see Cache management above)

---

## Emergency contacts

| Role | Contact |
|---|---|
| Owner / on-call | Alex Diachenko (andreidiachenko95@gmail.com) |
| Sentry workspace | https://sentry.io (Alex's account) |
| Railway workspace | https://railway.app (Alex's account) |
| Cloudflare | https://cloudflare.com (Alex's account) |

---

## Capacity expectations

Per SPEC §9 + PERFORMANCE_REPORT:
- 5,000 monthly visitors at MVP launch
- 50 concurrent users typical, 200 peak (Product Hunt spike day)
- p95 < 300ms server-side
- Lighthouse Performance ≥ 90, SEO ≥ 95

If actual traffic exceeds these consistently, the Phase-7 budget reserve allocates ~$10–20/mo for Postgres Pro tier and optionally Redis cache (per ADR-007 cutover threshold).
