# Performance testing — TrustGive

| Tool | What it covers |
|---|---|
| `k6-smoke.js` | API smoke test — runs in CI, sanity check on every deploy |
| `k6-load.js` | Load test — 200 concurrent users (SPEC §9 target) |
| `lighthouserc.json` | Lighthouse CI for frontend (Performance, A11y, SEO ≥95) |

## Running locally

```bash
# k6 (install: https://k6.io/docs/get-started/installation/)
k6 run k6-smoke.js
API_BASE_URL=http://localhost:8000 k6 run k6-load.js

# Lighthouse CI
npm install -g @lhci/cli
lhci autorun --config=./lighthouserc.json
```

## CI integration

`.github/workflows/perf.yml`, **weekly on Sunday 03:00 UTC** — not on every PR,
despite what this file used to say. `workflow_dispatch` runs it on demand and
accepts an `api_url` input.

### It was red for eight weeks and nobody was told anything true

From at least 21 June to 9 August 2026 every scheduled run failed, and the API
was healthy the whole time: p95 of 11ms against thresholds of 300 and 400ms,
7527 of 7527 checks passing.

`k6-load.js` hard-coded four charity slugs, and one of them —
`doctors-without-borders` — had been renamed to `msf-usa`. A quarter of the
detail traffic 404ed, which is 7.3% of all requests, which crossed the 2%
`http_req_failed` threshold. Exit code 99, every Sunday, for a site that was
fine.

Two rules came out of it, and they apply to any test written here:

- **Do not keep a copy of the catalogue in a test.** Copies go stale silently.
  `setup()` now reads real slugs from the API before the load phase begins.
- **One definition of failure per script.** The old check said "detail 200 or
  404" while the threshold counted every non-2xx as a failure, so the script
  disagreed with itself and the stricter half won. With slugs the catalogue
  handed us moments earlier, a 404 is a real fault, and the check now says so.

A scheduled job that always fails is training its reader to ignore it. Check
`gh run list --workflow perf.yml` occasionally, rather than waiting for the
failure mail to mean something.

## Targets

Per SPEC §9:
- API search/filter response p95 < 300ms server-side (catalog endpoint)
- Time to interactive < 2.5s on 4G mobile
- Lighthouse Performance ≥ 90
- Lighthouse SEO ≥ 95
- Concurrent users: 200 peak, 5K monthly visitors v1
