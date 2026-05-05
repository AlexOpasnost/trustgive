/**
 * Load test — simulate 200 concurrent users browsing the catalog.
 * SPEC §9 target: handle 200 concurrent users with p95 < 300ms server-side.
 *
 * Run: k6 run k6-load.js
 */
import http from "k6/http"
import { check, sleep } from "k6"

const BASE = __ENV.API_BASE_URL || "http://localhost:8000"

export const options = {
  stages: [
    { duration: "30s", target: 50 }, // ramp to 50 VUs
    { duration: "1m", target: 200 }, // hold at 200 for 1 min
    { duration: "30s", target: 0 }, // ramp down
  ],
  thresholds: {
    http_req_failed: ["rate<0.02"], // <2% failures
    "http_req_duration{endpoint:catalog}": ["p(95)<300"], // SPEC target
    "http_req_duration{endpoint:detail}": ["p(95)<400"], // detail is heavier
  },
}

const SLUGS = ["givedirectly", "heifer-international", "oxfam-america", "doctors-without-borders"]

export default function () {
  // 70% of traffic: catalog browsing
  if (Math.random() < 0.7) {
    const country = ["", "US", "GB"][Math.floor(Math.random() * 3)]
    const url = country
      ? `${BASE}/api/charities/?country=${country}&page_size=20`
      : `${BASE}/api/charities/?page_size=20`
    const res = http.get(url, { tags: { endpoint: "catalog" } })
    check(res, { "catalog 200": (r) => r.status === 200 })
  } else {
    // 30%: charity detail
    const slug = SLUGS[Math.floor(Math.random() * SLUGS.length)]
    const res = http.get(`${BASE}/api/charities/${slug}/`, { tags: { endpoint: "detail" } })
    check(res, { "detail 200 or 404": (r) => r.status === 200 || r.status === 404 })
  }

  sleep(Math.random() * 2 + 0.5) // 0.5-2.5s think time
}
