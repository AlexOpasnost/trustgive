# 02 — Architecture

## System overview

```
                          ┌──────────────────────────┐
                          │   Cloudflare CDN edge    │   ←── browser cache (Cache-Control)
                          │   (cache + WAF + DNS)    │
                          └─────────┬─────────┬──────┘
                                    │         │
                  /api/*  →─────────┘         └────→  static assets
                                    │
                                    ▼
              ┌──────────────────────────────────────────┐
              │         Railway (Docker)                  │
              │   ┌────────────────────────────────────┐  │
              │   │  Django 6 + DRF (gunicorn)         │  │
              │   │   - drf-spectacular                │  │
              │   │   - django-cachalot (LocMem)       │  │
              │   │   - python-json-logger             │  │
              │   │   - Sentry SDK                     │  │
              │   └─────────────┬──────────────────────┘  │
              │                 │                          │
              │   ┌─────────────▼──────────────────────┐  │
              │   │  PostgreSQL 17                     │  │
              │   │   - pg_trgm + unaccent             │  │
              │   │   - GIN indexes (cause_tags, FTS)  │  │
              │   │   - Single-trigger search_vector   │  │
              │   │     + name_trgm update             │  │
              │   └────────────────────────────────────┘  │
              └──────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
    ProPublica API           Every.org API         CharityBase.uk
    (free, no key)           (free, sign-up)       (free, no key)
              │                     │                     │
              └──── ETL nightly ────┴────────────────────┘
                  (Django mgmt commands via cron)


  ┌───────────────────────────────────────────────────────┐
  │  Cloudflare Pages — React 19 SPA (immutable + edge)   │
  │   - Vite build, manual chunks                         │
  │   - Tailwind v4 design tokens                         │
  │   - Hugeicons Free                                    │
  │   - i18next EN+RU                                     │
  │   - TanStack Query → /api/*                           │
  └───────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────┐
  │  Observability                               │
  │   - Sentry (free tier, 5K errors/mo)         │
  │   - PostHog (frontend client + server mirror │
  │     for donation_redirect — adblock-resist)  │
  │   - UptimeRobot on /api/health/              │
  │   - Railway built-in logs + metrics          │
  └──────────────────────────────────────────────┘
```

## Request flow — typical "user opens charity detail page"

1. Browser hits `https://trustgive.org/charities/givedirectly`
2. Cloudflare Pages serves the React SPA + assets (cached, ~10ms)
3. SPA mounts; `CharityDetailPage` calls `useQuery(['charity', 'givedirectly'])`
4. `api.getCharity('givedirectly')` → `GET https://api.trustgive.org/api/charities/givedirectly/`
5. Cloudflare CDN proxies to Railway origin (cache hit if recent — typical ~5ms)
6. Origin: Django middleware `RequestIDMiddleware` generates UUID4, attaches to context + log records
7. `CharityViewSet.retrieve` runs `_resolve_slug()` with `prefetch_related` — single SQL query (or cachalot cache hit)
8. `CharityDetailSerializer` shapes response with `LocalizedSerializerField` emitting `{en, ru}` for every localised field
9. Response includes `X-Request-ID` header + `Cache-Control: public, s-maxage=3600`
10. Browser renders page; React Query caches result for 5 minutes (`staleTime`)

## Data flow — nightly ETL

1. GitHub Actions cron triggers at 02:00 UTC
2. `railway run python manage.py ingest_propublica --since=24h`
3. `ingest_propublica` opens `IngestionLog` row (status=running)
4. `ThrottledHTTPClient` fetches ProPublica organizations index (5 req/sec politeness)
5. Per record:
   - `_find_or_create_charity()` runs **tiered dedup**: hard match → fuzzy auto (≥0.92) → fuzzy flag (0.85-0.92)
   - `transaction.atomic()` + `select_for_update(skip_locked=True)` on SourceMapping
   - `raw_data_hash` short-circuit elides identical re-imports (turns 1.8M record sync into ~5K-record diff)
   - Postgres trigger on Charity update repopulates `search_vector` + `name_trgm` atomically
   - `Charity.post_save` signal fires → debounced (60s) Cloudflare cache purge
6. Errors collected per-record into `IngestionLog.errors` JSONB
7. Final status: `succeeded` / `partial` / `failed`; Sentry breadcrumb on partial/failed

## Technology choices — why

| Decision | Rationale | ADR |
|---|---|---|
| PostgreSQL 17 (single DB) | One database simplifies ops + free on Railway | ADR-001 |
| No auth in MVP | Anonymous discovery aligns with positioning; saves 1 week dev | ADR-002 |
| REST + drf-spectacular | CDN-cacheable; auto-generated TS client; familiar tooling | ADR-003 |
| Tiered fuzzy dedup ETL | Cross-registry collisions inevitable; hard match alone misses ~5% | ADR-004 |
| Postgres FTS + pg_trgm | $0; bilingual via single `simple` config; <1M records works | ADR-005 |
| LocalizedTextField JSONB | Adding 3rd language = no schema migration | ADR-006 |
| Cloudflare CDN + cachalot LocMem | No Redis cost; CDN absorbs traffic spikes | ADR-007 |
| Sentry + JSON logs + server-side PostHog mirror | Adblocker-resistant on conversion event | ADR-008 |

Full discussion: [`docs/adr/ADR-001` through `ADR-008`](../docs/adr/).

## Key abstractions

### `LocalizedTextField` (apps/core/fields.py)
JSONB-backed Django field storing `{en: str, ru: str, ...}`. Default factory returns both keys empty; `get_prep_value` ensures both are present on save. Used on every localised content field.

### `RequestIDMiddleware` + `RequestIDLogFilter`
UUID4 per request → contextvar → response header `X-Request-ID` + log record. The same `request_id` appears in every log line and every error envelope, making support workflow trivial.

### Single-trigger search update
One Postgres trigger reads JSONB `name->>'en'`/`'ru'` and updates BOTH `search_vector` (tsvector) AND `name_trgm` (text for fuzzy). Atomic with row writes — no orphan-state bugs at ETL scale. (KB-BACKEND-TRUSTGIVE-005)

### Server-side PostHog mirror
The donation_redirect event mirrors to PostHog server-side via `threading.Thread + queue.Queue` (no Celery). Resistant to adblockers — captures the conversion event that matters most. (KB-BACKEND-TRUSTGIVE-002)

## Open architectural items

- SSR/SSG for SEO landing pages — currently SPA; `react-snap` or Vike migration in Phase 4.5+
- Initial migration `0001_initial` checked into repo (REVIEW_REPORT H-001)
- CORS configuration in production (REVIEW_REPORT H-003)
- Cause `charity_count` denormalisation (REVIEW_REPORT L-003)
