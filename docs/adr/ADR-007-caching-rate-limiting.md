# ADR-007 — Caching strategy + rate limiting

- **Status**: Accepted
- **Date**: 2026-05-05
- **Deciders**: Backend Developer, per SPEC.md §9 + DEVOPS.md
- **Supersedes**: —

## Context

Workload reality:
- **>95% of requests are reads** of catalog or detail pages
- Underlying data refreshes nightly, not per-request
- Same anonymous response for every user (no auth, ADR-002)
- SPEC §9: search/filter response <300ms server-side, Lighthouse Performance ≥90, 200 concurrent users target
- $0/mo budget — no managed Redis on Railway free tier
- We do have Cloudflare in front (DEVOPS plan: Cloudflare Pages for frontend, Cloudflare proxy in front of api.trustgive.org)

We also have one write endpoint (`/api/events/donation-redirect/`) and an unauthenticated public surface — both abuse vectors. Rate limiting is mandatory.

## Decision

### Caching: three layers, no Redis in MVP

```
Browser cache (Cache-Control)
         │
         ▼
Cloudflare CDN edge cache (s-maxage)
         │
         ▼
django-cachalot ORM-result cache (in-process LRU per Django worker)
         │
         ▼
PostgreSQL (no shared query cache; relies on Postgres' own buffer cache)
```

#### Layer 1 — Cloudflare CDN edge cache

Per-endpoint `Cache-Control` headers (declared in API_SPEC.md §1):

| Endpoint | Cache-Control | Rationale |
|---|---|---|
| `/api/health/` | `no-store` | Always real-time |
| `/api/charities/` | `public, s-maxage=3600, stale-while-revalidate=86400` | 1h fresh, 24h stale-while-revalidate covers nightly ingestion gap |
| `/api/charities/{slug}/` | `public, s-maxage=3600, stale-while-revalidate=86400` | Same |
| `/api/charities/{slug}/source-documents/` | `public, s-maxage=86400` | Documents change ≤monthly |
| `/api/charities/compare/` | `public, s-maxage=3600` | Same as listing |
| `/api/causes/` | `public, s-maxage=86400` | Taxonomy changes rarely |
| `/api/feed.rss` | `public, s-maxage=3600` | Hourly refresh |
| `/api/seo/charities/{slug}/` | `public, s-maxage=3600, stale-while-revalidate=86400` | Same as detail |
| `/api/events/donation-redirect/` | `no-store` | POST, never cached |
| `/api/schema/`, `/api/docs/` | `public, s-maxage=3600` | Slow-changing, low traffic |

`Vary: Accept-Encoding, Accept-Language` on all cacheable endpoints to keep `?lang=en` and `?lang=ru` separate cache entries.

**Cache invalidation on ETL**: when a `Charity` is updated (post_save signal from `ingest_*` commands), call Cloudflare Cache API `purge_files` for the affected URLs:
- `/api/charities/{slug}/`
- `/api/charities/{slug}/source-documents/`
- `/api/seo/charities/{slug}/`
- Catalog URLs are NOT individually purged — TTL-only invalidation (1h max staleness is acceptable).

Cloudflare API credentials live in Railway Variables (`CF_API_TOKEN`, `CF_ZONE_ID`). Free tier supports 1K purge calls/day — sufficient for nightly ETL hitting 200–500 changed records.

#### Layer 2 — django-cachalot (ORM-result cache)

`pip install django-cachalot==2.6.3`. Wraps Django ORM `QuerySet.__iter__` and caches results keyed by SQL hash. Invalidated automatically on any model save.

Backing store: **`django.core.cache.backends.locmem.LocMemCache`** (in-process, per Django worker). No Redis needed.

Trade-off: Railway typically runs 1–3 worker processes for hobby tier; each worker has its own LocMem cache. Misses are cheap (Postgres is 5ms away on Railway internal network). When we scale to >5 workers AND see >50% miss rate in PostHog, upgrade to Redis (Phase-7 budget reserve).

Cachalot configuration (in `settings/base.py`):
```python
CACHALOT_ENABLED = True
CACHALOT_TIMEOUT = 60 * 60      # 1 hour
CACHALOT_DATABASES = ['default']
CACHALOT_UNCACHABLE_TABLES = (   # Don't cache; needs to be real-time
    'ingestion_log',
    'donation_redirect_event',
)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'trustgive-default',
        'TIMEOUT': 3600,
        'OPTIONS': {'MAX_ENTRIES': 5000},
    }
}
```

#### Layer 3 — Postgres buffer cache

Standard Postgres behaviour; no app-level config. Railway Postgres has ~256MB shared_buffers on hobby tier — enough for the working set.

### Rate limiting: DRF throttling, no extra infrastructure

```python
# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/min',
        'donation_redirect': '10/min',  # custom
    },
}
```

```python
# apps/events/throttling.py
class DonationRedirectThrottle(AnonRateThrottle):
    scope = 'donation_redirect'
    cache_format = 'throttle_donation_redirect_%(ident)s'
    # Keys on REMOTE_ADDR (DRF default for AnonRateThrottle)
```

Per-view assignment:
```python
# apps/events/views.py
class DonationRedirectView(APIView):
    throttle_classes = [DonationRedirectThrottle]
```

`/api/health/` and `/api/schema/` are exempt (`throttle_classes = []`).

**Throttle backend**: same LocMemCache as cachalot. With multi-worker, this means the rate limit is per-worker — a determined attacker with even 3 workers' worth of capacity gets 30/min, not 10/min. Acceptable for the abuse profile (we're not protecting financial transactions). Real abuse mitigation comes from Cloudflare's WAF in front (free tier includes basic bot detection).

When we move to Redis (or upgrade to Memcached), throttle counters become globally consistent — `CACHE_BACKEND = 'django.core.cache.backends.redis.RedisCache'` and DRF picks it up automatically.

### 429 response shape

Per API_SPEC.md §5:
```json
{"error": {"code": "RATE_LIMITED", "message": "Too many requests",
           "details": {"retry_after_seconds": 47}, "request_id": "..."}}
```
Plus the standard `Retry-After: 47` HTTP header.

## Consequences

### Positive
- **Effectively free** — Cloudflare free tier + LocMem cache, no Redis bill.
- **Edge cache absorbs traffic spikes**: Product Hunt launch could send 5K visitors in an hour; Cloudflare serves ~99% of catalog hits without touching Django.
- **Fast invalidation** for known-changed charities (Cloudflare API purge), TTL fallback for catalog.
- **DRF throttling is one-line per view** — minimal code surface.
- **Search and filter SPEC target (<300ms)** is met for warm-cache requests in the 5–30ms range.

### Negative
- **Per-worker LocMem cache** is not globally consistent — minor inefficiency. Acceptable until concrete data shows otherwise.
- **Cache stampede on TTL expiry**: when a popular catalog query's cache entry expires, 5+ workers might all hit Postgres at once. Mitigated by cachalot's slight TTL jitter + `stale-while-revalidate` at the edge (Cloudflare serves stale while one origin request refreshes).
- **Cloudflare cache purge API** has 1K/day limit on free plan — sufficient now, but bulk re-ingestion would need bulk purge. Workaround: use `purge_everything` (rate-limited to 1/day) for full re-ingestion days.
- **Throttle bypass** via IP rotation is possible. Cloudflare WAF + future Cloudflare Turnstile (free) close the gap if abuse becomes real.

### Neutral
- All cache decisions are non-breaking: turning a layer off (`CACHALOT_ENABLED = False`, removing `Cache-Control`) does not alter API contract.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| **Redis cache layer** | Railway free tier doesn't include managed Redis; paid Redis = $5–10/mo. cachalot + LocMem covers MVP; promote to Redis only if cachalot's per-worker locality bites. |
| **Memcached** | Same network-hop cost as Redis; no advantages over LocMem for single-host workers; weaker feature set than Redis. |
| **Varnish in front of Django** | Cloudflare already plays this role at the edge — running our own Varnish is duplicative and adds an ops burden. |
| **Per-view `@cache_page` Django middleware** | Coarse — keys on full URL, ignores ORM-level reuse opportunities. cachalot is finer-grained. |
| **No caching, scale Postgres up instead** | Misses the obvious win — most requests are identical and have no business hitting the DB at all. |
| **No rate limiting** | Single endpoint allowing POSTs without auth + no throttle = trivial PostHog event flood vector. |
| **`django-ratelimit`** | Functionally equivalent to DRF's built-in throttle. DRF throttle integrates with the existing API stack cleanly; no extra dependency. |
| **Cloudflare Workers for rate limit** | Adds an edge-compute dependency outside our framework. DRF throttle suffices. |

## Implementation hooks (Phase 3)

- `pip install django-cachalot==2.6.3`
- `INSTALLED_APPS += ['cachalot']`
- Cache settings as above
- DRF throttle classes + scopes
- Custom `DonationRedirectThrottle` in `apps/events/throttling.py`
- `apps/core/cdn.py`: `purge_charity(slug)` helper using Cloudflare API
- post_save signal: `Charity.post_save → purge_charity(instance.slug)` (debounced if many charities updated in one ETL run — batch into one call per 100 records)
- Add `Cache-Control` headers via DRF response middleware or per-view decorator

## Notes / forward references

- Headers per endpoint: API_SPEC.md §1
- 429 envelope: API_SPEC.md §5
- Health-check endpoint exempt from throttle: ADR-008
