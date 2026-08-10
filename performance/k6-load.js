/**
 * Load test — simulate 200 concurrent users browsing the catalog.
 * SPEC §9 target: handle 200 concurrent users with p95 < 300ms server-side.
 *
 * Run: k6 run k6-load.js
 *
 * Why the slugs are fetched rather than listed
 * --------------------------------------------
 * This job failed every week from at least 21 June to 9 August 2026 — eight
 * consecutive red runs — and the site was never the problem. p95 came in at
 * 11ms against limits of 300 and 400ms, and 7527 of 7527 checks passed.
 *
 * It failed because the script hard-coded four slugs and one of them,
 * `doctors-without-borders`, had been renamed to `msf-usa`. A quarter of the
 * detail traffic 404ed: 30% detail × 25% dead ≈ 7.3% of all requests, which is
 * exactly the `http_req_failed` rate that crossed the 2% threshold.
 *
 * Two defects, and the second is the one worth remembering:
 *
 *   1. A fixed list of slugs is a copy of the catalogue, and copies go stale
 *      silently. The list is now read from the API at startup, so it cannot
 *      disagree with what is actually published.
 *
 *   2. The script held two contradictory definitions of failure. The check said
 *      "detail 200 or 404" — a 404 is fine — while the `http_req_failed`
 *      threshold counts every non-2xx as a failure. One of them had to be
 *      wrong, and it was the check: with real slugs, a 404 on a charity the
 *      catalogue just handed us is a genuine fault and should fail the run.
 *
 * The eight red runs are the real lesson. A scheduled job that has never been
 * green teaches its reader to ignore it, and this one was reporting a
 * comfortably healthy API as broken every Sunday.
 */
import http from "k6/http"
import { check, fail, sleep } from "k6"

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

/**
 * Real slugs, taken from the catalogue itself once before the run.
 *
 * Runs outside the load phase, so it costs nothing in the measurement, and it
 * fails loudly: if the API cannot hand us a page of charities there is no point
 * measuring how fast it serves them.
 */
export function setup() {
  const res = http.get(`${BASE}/api/charities/?page_size=20`)
  if (res.status !== 200) {
    fail(`setup: catalogue returned ${res.status}; cannot pick slugs to test`)
  }
  const slugs = (res.json("results") || []).map((c) => c.slug).filter(Boolean)
  if (slugs.length === 0) {
    fail("setup: catalogue returned no charities; nothing to load-test")
  }
  return { slugs }
}

export default function (data) {
  // 70% of traffic: catalog browsing
  if (Math.random() < 0.7) {
    const country = ["", "US", "GB"][Math.floor(Math.random() * 3)]
    const url = country
      ? `${BASE}/api/charities/?country=${country}&page_size=20`
      : `${BASE}/api/charities/?page_size=20`
    const res = http.get(url, { tags: { endpoint: "catalog" } })
    check(res, { "catalog 200": (r) => r.status === 200 })
  } else {
    // 30%: charity detail. The slug came from the catalogue moments ago, so
    // anything but 200 is a real fault — no 404 escape hatch here.
    const slug = data.slugs[Math.floor(Math.random() * data.slugs.length)]
    const res = http.get(`${BASE}/api/charities/${slug}/`, { tags: { endpoint: "detail" } })
    check(res, { "detail 200": (r) => r.status === 200 })
  }

  sleep(Math.random() * 2 + 0.5) // 0.5-2.5s think time
}
