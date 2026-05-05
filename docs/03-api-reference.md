# 03 — API reference

> **Authoritative source**: [`API_SPEC.md`](../API_SPEC.md) (OpenAPI 3.1 spec) + the auto-generated Swagger UI at `/api/docs/` once the backend is running.

This document is a **summary** for orientation. For exact field names, schemas, and example payloads, see those two sources.

## Base URL

| Env | URL |
|---|---|
| Production | `https://api.trustgive.org` (planned) |
| Local dev | `http://localhost:8000` |

## Authentication

**None in MVP** (per ADR-002). All public endpoints accept anonymous requests.

## Content type

- Request: `application/json` (where applicable)
- Response: `application/json` (default) or `application/rss+xml` (`/api/feed.rss`)

## Endpoint summary

| Method | Path | Purpose | Cacheable | Throttle |
|---|---|---|---|---|
| GET | `/api/health/` | Liveness probe | No | none |
| GET | `/api/charities/` | Catalog list (faceted) | 1h CDN | 60/min |
| GET | `/api/charities/{slug}/` | Charity detail | 1h CDN | 60/min |
| GET | `/api/charities/{slug}/source-documents/` | Source documents | 24h CDN | 60/min |
| GET | `/api/charities/compare/?slugs=a,b,c` | Side-by-side (max 3) | 1h CDN | 60/min |
| GET | `/api/causes/` | Cause taxonomy (EN+RU) | 24h CDN | 60/min |
| GET | `/api/feed.rss` | RSS of newly added | 1h CDN | 60/min |
| GET | `/api/seo/charities/{slug}/` | SEO landing payload | 1h CDN | 60/min |
| POST | `/api/events/donation-redirect/` | Outbound-click logging | No | 10/min |
| GET | `/api/schema/` | OpenAPI 3.1 doc | 1h CDN | none |
| GET | `/api/docs/` | Swagger UI HTML | 1h CDN | none |

## Filters on `/api/charities/`

- `cause` — repeatable, e.g. `?cause=animals&cause=climate`
- `country` — `US` / `GB` / `RU`
- `size` — `small` (<$100K), `medium` ($100K-$1M), `large` (>$1M)
- `verification_status` — `verified` / `listed` / `stale`
- `badges` — comma-separated badge slugs
- `q` — free-text search (Postgres FTS + pg_trgm)
- `lang` — `en` / `ru`
- `sort` — `most_recent_filing` (default) / `largest_revenue` / `highest_program_pct` / `alphabetical`
- `page`, `page_size` (default 20, max 100)

## Localised fields

Every localised field uses the **nested object pattern**:

```json
"name": {"en": "GiveDirectly", "ru": "GiveDirectly"},
"tagline": {"en": "Cash transfers", "ru": "Денежные переводы"}
```

Both keys always present, even if empty. UI falls back from missing key to the other.

## Error envelope

Uniform across all endpoints:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {"field": "slug", "issue": "Invalid slug format"},
    "request_id": "8b1f9d6a-3c4d-4e5f-9a8b-7c6d5e4f3a2b"
  }
}
```

Standard error codes:
- `VALIDATION_ERROR` (400)
- `NOT_FOUND` (404)
- `RATE_LIMITED` (429) — `details.retry_after_seconds` populated, `Retry-After` header set
- `SERVICE_UNAVAILABLE` (503) — only `/api/health/` returns this in normal ops
- `INTERNAL_ERROR` (500) — `details.sentry_id` for support correlation

## Request tracing

Every response includes header `X-Request-ID: <uuid4>`. The same UUID appears in:
- Every JSON log line emitted during request handling (Sentry breadcrumbs, Django logs)
- The error envelope (`error.request_id`)

When a user reports an issue, the `X-Request-ID` value is the only thing you need to grep logs.

## Rate limiting

- Anonymous default: **60 requests/min per IP** (DRF `AnonRateThrottle`)
- `/api/events/donation-redirect/`: **10 requests/min per IP** (custom `DonationRedirectThrottle`)
- `/api/health/`, `/api/schema/`, `/api/docs/`: no throttle

429 response shape:
```json
{"error": {"code": "RATE_LIMITED", "message": "Too many requests. Retry after 47s.",
           "details": {"retry_after_seconds": 47}, "request_id": "..."}}
```

## Generating a typed TypeScript client

Once backend is running:

```bash
cd frontend/web
npx openapi-typescript http://localhost:8000/api/schema/ -o src/api/schema.d.ts
```

Then refactor `src/lib/api.ts` to use `openapi-fetch` against the generated `paths` object — full type safety from spec to UI.

## CORS

⚠ **Not yet configured in production** (per REVIEW_REPORT H-003). For local dev, the Vite dev-server proxy handles CORS by routing `/api/*` through the same origin. Production cross-origin requires `django-cors-headers` setup before launch.

## Worked examples

### List 20 verified animal-welfare US charities

```bash
curl "http://localhost:8000/api/charities/?country=US&cause=animals&verification_status=verified&page_size=20"
```

### Get charity detail in Russian

```bash
curl "http://localhost:8000/api/charities/givedirectly/?lang=ru"
```

### Compare 3 charities

```bash
curl "http://localhost:8000/api/charities/compare/?slugs=givedirectly,heifer-international,oxfam-america"
```

### Log a donation redirect (frontend does this; included for completeness)

```bash
curl -X POST "http://localhost:8000/api/events/donation-redirect/" \
  -H "Content-Type: application/json" \
  -d '{
    "client_event_id": "8b1f9d6a-3c4d-4e5f-9a8b-7c6d5e4f3a2b",
    "charity_slug": "givedirectly",
    "lang": "en",
    "source_page": "detail"
  }'
# → 202 Accepted {"status": "accepted"}
```
