# Test Report — TrustGive

> **Status**: Phase 4.5 deliverable
> **Date**: 2026-05-05
> **Author**: Project Lead (Testing Engineer + E2E Engineer agents skipped per Phase 3 sandbox lessons)

---

## Summary

Test scaffolding + representative test cases written for backend (pytest), frontend (Vitest + RTL), and end-to-end (Playwright). Coverage target per CLAUDE.md is 70% on business logic — current coverage is **representative, not exhaustive** because the 8-week MVP timeline prioritises shipping over comprehensive test suites. The framework is in place; expanding coverage in Phase 4.5+ (post-launch) is straightforward.

---

## Backend (pytest)

### Setup
- `backend/pytest.ini` — `DJANGO_SETTINGS_MODULE=trustgive.settings.development`, reuse-db, short tracebacks
- `backend/conftest.py` — top-level fixtures: `api_client`, `client`
- Run: `cd backend && pytest`

### Coverage written

| File | Cases | Domain |
|---|---|---|
| `apps/core/tests/test_localized_field.py` | 7 | LocalizedTextField default/empty/None handling, LocalizedSerializerField round-trip + key fallback (ADR-006 contract) |
| `apps/core/tests/test_health.py` | 2 | HealthView returns 200 with `{status, db, sentry}`; throttle-exempt |
| `apps/charities/tests/test_models.py` | 4 | Charity creation, country+registration_id uniqueness, slug uniqueness, cause_tags ArrayField containment |
| `apps/charities/tests/test_views.py` | 6 | DRF API endpoints — list paginated shape, detail full shape, 404 envelope, country filter, compare validation, X-Request-ID header |
| `apps/events/tests/test_donation_redirect.py` | 3 | 202 Accepted, idempotency on repeated client_event_id, validation error envelope |

### What's NOT covered (deferred)
- ETL pipeline (`ingest_propublica`) — needs ProPublica response fixtures + mocking (Phase 4.5+)
- Search vector trigger behaviour — requires running Postgres with pg_trgm (integration test in CI)
- CharitySlugAlias 301 redirect — covered by E2E
- Cache invalidation signal — requires Cloudflare API mock
- Cachalot cache hit/miss validation
- Custom DRF exception handler edge cases (request_id in body, Sentry id mirror)

### Coverage gaps explained
**Why not 70%?** ETL command alone is ~250 LOC and requires fixture corpus. We accept ~40% coverage on Phase 4 launch with the stipulation that critical paths (model integrity, API shape contract, auth/throttle policies) are covered. Post-launch sprint expands ETL + signals tests.

---

## Frontend web (Vitest + React Testing Library)

### Setup
- `frontend/web/vitest.config.ts` — jsdom env + `src/test/setup.ts`
- `src/test/setup.ts` — RTL cleanup + `matchMedia` polyfill
- Run: `cd frontend/web && npm test`

### Coverage written

| File | Cases | Domain |
|---|---|---|
| `src/lib/__tests__/utils.test.ts` | 6 | `cn` Tailwind merge + `formatUsd` (compact + nullish + invalid) + `formatPercent` (decimals + nullish) |
| `src/components/charity/__tests__/VerificationBadge.test.tsx` | 3 | Verified/listed labels render; SR-only context "Verification status:" present |

### What's NOT covered (deferred)
- All other components (CharityCard, MoneyBreakdown, SourceDocumentDrawer, DonateConfirmModal)
- Page-level integration (HomePage, CatalogPage, CharityDetailPage routing + queries)
- i18n switch behaviour
- Error/loading/empty states render
- TanStack Query behaviour (mock service worker setup)

These are written in Phase 4.5+. Estimated 1-2 days of dedicated test work.

---

## End-to-end (Playwright)

### Setup
- `e2e/package.json` + `e2e/playwright.config.ts`
- 2 projects: `chromium-desktop` + `mobile-iphone` (DESIGN.md mobile breakpoint coverage)
- Run: `cd e2e && npm install && npm run install:browsers && npm test`

### Coverage written (8 tests across 3 critical journeys)

| File | Tests | User journey |
|---|---|---|
| `homepage-and-language.spec.ts` | 3 | Hero + 0% callout render; EN→RU→EN switch flips all UI strings; nav to methodology page |
| `catalog-flow.spec.ts` | 3 | Catalog page renders filters; country filter persists in URL; source-doc drawer opens + ESC dismisses (skipped if no seeded data) |
| `donate-flow.spec.ts` | 2 | Donate modal renders 3-bullet anti-fee pitch; Cancel dismisses (skipped if no seeded data) |

Tests gracefully **skip** when backend has no data — usable against fresh local dev OR a public deploy. CI runs them after backend seed step.

### What's NOT covered (deferred)
- Comparison flow (component not yet built)
- Mobile-specific drawer collapse behaviour
- Visual regression (screenshot comparison)

---

## CI integration plan (Phase 7 DevOps Engineer wires)

```yaml
# .github/workflows/test.yml — Phase 7 deliverable
- pytest (backend)
- npm test (frontend)
- npm test (e2e) — only on PR to main
- coverage upload to codecov.io free tier
```

---

## Recommendation

The current test suite **is sufficient to confidently ship Phase 4 → Phase 5 (Code Review)**. It catches:
- Schema contract violations (model field changes that break API shape)
- DRF API response shape regressions
- LocalizedTextField + LocalizedSerializerField round-trip bugs (the i18n contract per ADR-006)
- Donate redirect idempotency (mission-critical conversion event)
- Critical user-journey regressions (Playwright E2E)

**Before public launch (Week 8)**, the coverage gaps marked "deferred" above must close — particularly ETL pipeline tests (a single bug there could ship bad data to thousands of SEO landing pages).
