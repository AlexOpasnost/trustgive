/**
 * Smoke test — sanity check that the API is responsive.
 * Runs in CI on every deploy; should always pass.
 *
 * Run: k6 run k6-smoke.js
 */
import http from "k6/http"
import { check, sleep } from "k6"

const BASE = __ENV.API_BASE_URL || "http://localhost:8000"

export const options = {
  vus: 1,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.01"], // <1% failures
    http_req_duration: ["p(95)<500"], // 95% < 500ms
  },
}

export default function () {
  const health = http.get(`${BASE}/api/health/`)
  check(health, {
    "health 200": (r) => r.status === 200,
    "health body has status": (r) => r.json("status") === "ok",
  })

  const list = http.get(`${BASE}/api/charities/?page_size=20`)
  check(list, {
    "catalog 200": (r) => r.status === 200,
    "catalog has results": (r) => Array.isArray(r.json("results")),
  })

  sleep(1)
}
