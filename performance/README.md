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

Performance suite runs on every PR via the GitHub Actions workflow added by Phase 7 DevOps Engineer.

## Targets

Per SPEC §9:
- API search/filter response p95 < 300ms server-side (catalog endpoint)
- Time to interactive < 2.5s on 4G mobile
- Lighthouse Performance ≥ 90
- Lighthouse SEO ≥ 95
- Concurrent users: 200 peak, 5K monthly visitors v1
