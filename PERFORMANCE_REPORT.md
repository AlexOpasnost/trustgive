# Performance Report — TrustGive

> **Status**: Phase 4.5 deliverable (methodology + targets; live-deploy benchmarks pending)
> **Date**: 2026-05-05
> **Author**: Project Lead (Performance Engineer agent skipped per sandbox lessons)
> **Targets**: SPEC §9 — search/filter p95 < 300ms server-side, Lighthouse Performance ≥ 90, 200 concurrent users

---

## Summary

The performance test infrastructure is in place (`performance/k6-smoke.js`, `performance/k6-load.js`, `performance/lighthouserc.json`) with thresholds matching SPEC §9. Live benchmark numbers are pending **first staging deploy** (Phase 7) because there is no running backend to measure today. This report documents the methodology + expected baseline derived from the architecture, and flags the known performance risks the load test will validate.

---

## 1. API performance — k6 load test

### Smoke (`k6-smoke.js`)
- 1 VU, 30 seconds
- Hits `/api/health/` and `/api/charities/?page_size=20`
- Thresholds: <1% failures, p95 < 500ms
- **Run on every deploy as a "did anything obviously break?" gate**

### Load (`k6-load.js`)
- Stages: ramp 50 → 200 VUs → ramp down (2 min total)
- Traffic mix: 70% catalog browse, 30% charity detail
- Thresholds: catalog p95 < 300ms (SPEC), detail p95 < 400ms (heavier prefetches), <2% failures
- Tags requests by endpoint (`endpoint:catalog`, `endpoint:detail`) so per-endpoint p95 is asserted independently

### Expected baselines (architecture-derived)

| Endpoint | Cold (no cache) | Warm (cachalot + Postgres buffer) | CDN cache hit |
|---|---|---|---|
| `/api/health/` | 5–10ms | n/a (no cache) | n/a (no-store) |
| `/api/charities/` (no filters) | 30–80ms | 5–15ms | <5ms |
| `/api/charities/` (with filters) | 50–120ms | 15–30ms | <5ms |
| `/api/charities/{slug}/` | 40–100ms | 20–40ms | <5ms |
| `/api/charities/{slug}/source-documents/` | 20–50ms | 10–20ms | <5ms |
| `/api/charities/compare/?slugs=...` | 80–200ms | 30–60ms | <5ms |

The Cloudflare CDN cache (per ADR-007) absorbs ~99% of catalog hits at <5ms, so SPEC's 300ms target is **easily met for repeated traffic**. Real concern is cold-cache + filter-heavy queries — that's where the load test focuses.

---

## 2. Database performance

### Indexing strategy validation (per ADR-001)

All catalog filter columns have indexes:
- `cause_tags` — GIN (array containment)
- `country`, `verification_status`, `size_bucket`, `is_stale` — btree
- `last_filed_date`, `total_revenue_usd` — btree DESC for sorts
- `(charity_id, year DESC)` composite on Financial — index-only scan for "latest filing"
- `search_vector` — GIN
- `name_trgm` — GIN(gin_trgm_ops)

Expected query plans for typical catalog filter (US + verified + cause=animals + sort by recent):
```
Index Scan + Bitmap And on charity_country_idx + charity_verstatus_idx + charity_causes_gin
→ Sort by last_filed_date DESC (already btree DESC)
→ Limit 20
```

Should execute in 10–40ms on a 1.2M row table on Railway hobby tier Postgres.

### Known risks the load test will surface

1. **Pagination `COUNT(*) OVER()` slow on filtered queries** — DRF's `PageNumberPagination` runs an extra COUNT query. With aggressive filtering this is fine (small result count), with empty filters it's a 1.2M-row count. Mitigation if observed: cursor pagination opt-in via `?cursor=...` parameter (deferred per API_SPEC §7).

2. **N+1 on charity detail** — `Charity → financial_history → trust_badges → source_documents → news_mentions`. The detail viewset uses `prefetch_related` (`apps/charities/views.py:_resolve_slug`) so this is mitigated. **Verify with `django-debug-toolbar` SQL panel during dev**.

3. **Cachalot LocMem per-worker** — multi-worker Railway deploys mean each worker has its own cache. Acceptable until we observe >50% miss rate in PostHog. Path forward: Redis cache at $5/mo.

---

## 3. Frontend performance — Lighthouse CI

### Setup (`performance/lighthouserc.json`)
- 3 URLs audited: `/`, `/charities`, `/methodology`
- 3 runs each (median reported)
- Desktop preset
- Asserts: Performance ≥ 0.9, A11y ≥ 0.95, Best Practices ≥ 0.9, SEO ≥ 0.95

### Bundle size targets (per FRONTEND.md §8)

| Chunk | Target gzipped |
|---|---|
| `react-vendor` | <150 KB |
| `query-vendor` | <30 KB |
| `ui-vendor` (Radix) | <40 KB |
| `icons-vendor` (Hugeicons subset) | <10 KB |
| `i18n-vendor` | <30 KB |
| Initial app code | <50 KB |
| **Total initial download** | **~300 KB gzipped** |

Recharts is lazy-imported only on charity detail page → ~80 KB shows up only when needed.

### Initial paint expectations
- Time to First Byte: <200ms (Cloudflare Pages global edge)
- First Contentful Paint: <1.0s on 4G
- Largest Contentful Paint: <2.0s on 4G (homepage hero text + 0% callout)
- Time to Interactive: <2.5s on 4G (SPEC target)
- Cumulative Layout Shift: <0.1 (no late-loaded images shifting hero)

### Known risks
- **Google Fonts (Inter + Source Serif + Geist Mono) preload** — 3 font families loaded with `display=swap`. Worst case: ~200KB on first paint. Mitigation if FCP suffers: subset to latin+cyrillic only (already configured), self-host fonts on Cloudflare Pages instead of Google Fonts CDN.

- **Hugeicons tree-shaking** — relies on consumer-side imports. We import only ~10 icons explicitly so this works. Monitor `dist/assets/icons-vendor-*.js` size on each build.

---

## 4. SEO performance

Per SPEC §9: Lighthouse SEO ≥ 95. The auto-generated SEO landing pages (per API_SPEC `/api/seo/charities/{slug}/`) target long-tail "Is X legitimate?" queries.

**Known SEO gap in Phase 4**: SPA without SSR. Crawlers see an empty `<div id="root">`. Mitigation strategy (Phase 4.5+):
1. **Option A**: `react-snap` or `vite-plugin-prerender` — pre-renders SPA routes to static HTML at build time. Simplest, ships static `dist/`.
2. **Option B**: Migrate to **Vike** (formerly vite-plugin-ssr) — full SSR/SSG with React, Cloudflare Pages compatible.
3. **Option C**: Cloudflare Workers with HTML rewriter — fetch SEO endpoint, inject critical content into `<head>`.

Decision deferred — Phase 4.5+ Frontend pass picks.

---

## 5. Profiling tools wired

### Backend
- `django-debug-toolbar` — added in development.py (Phase 3 — actually deferred; Phase 4.5+ task)
- Postgres query logging via `LOGGING['django.db.backends']` (currently WARNING level — bump to DEBUG locally to see SQL)
- N+1 detection: run `python manage.py runserver`, hit endpoint, check console for repeated SELECTs

### Frontend
- Vite build report: `npm run build` shows chunk sizes + per-asset gzip
- React DevTools profiler (browser extension)

---

## 6. Pre-launch performance gate (Week 7-8)

Before public launch, the load test must pass against **production-equivalent staging**:
- 200 VUs hitting Railway-deployed API
- Cloudflare CDN warm
- Real Postgres with ~1K seeded charities
- All thresholds in `k6-load.js` met

If thresholds are missed, the prioritised mitigation list (cheapest first):
1. Increase Cloudflare cache TTLs from 1h to 4h
2. Add `?fields=` query parameter to thin catalog response payload
3. Pre-warm cache: scheduled cron hits top-100 catalog filter combos every 30 min
4. Move cache backend to Redis ($5/mo)
5. Migrate search to Meilisearch (per ADR-005 cutover threshold)

---

## 7. Open items

- **Live benchmark numbers** — pending first Railway staging deploy
- **Lighthouse CI run against deployed frontend** — pending Cloudflare Pages deploy
- **N+1 audit using django-debug-toolbar** — Phase 4.5 follow-up
- **Realistic load with 50K-row seed** — pending bulk ETL run
- **Continuous performance regression in CI** — added by DevOps Engineer in Phase 7
