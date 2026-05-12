/**
 * Image proxy / thumbnail helper.
 *
 * v3.16 — all third-party images route through the trustgive-web Worker at
 * `/img/v1?url=X&w=N`. The Worker (worker/index.ts):
 *   - rewrites Wikimedia URLs to the policy-compliant `/thumb/.../{N}px-...`
 *     endpoint, sending a real User-Agent that meets Wikimedia's UA-policy;
 *   - falls back to the original URL when the thumb endpoint returns 404;
 *   - caches at Cloudflare edge for 30 days;
 *   - sets `Cross-Origin-Resource-Policy: cross-origin` + CORS headers so
 *     Chrome's ORB never blocks the response.
 *
 * Same-origin from the browser's POV (proxy is `/img/v1` on trustgive.org)
 * which means no CORS preflight at all — the browser treats the image as
 * first-party. ORB does not apply to same-origin responses.
 *
 * Page-weight win vs v3.15.2: Wikimedia originals are 3-8 MB per file; the
 * Worker now returns the 800/1024/1600 px thumbnail at ~80-300 KB each.
 * Catalog page (60 cards × 800 px thumbs) drops from ~250 MB raw to ~5-12 MB
 * cached.
 *
 * SVG: still passes through unchanged (already small; proxying just adds
 * a hop). Most charity logos are SVG.
 */

const PROXY_BASE = "/img/v1?"

export function wikimediaThumb(
  url: string | null | undefined,
  widthPx: number,
): string {
  if (!url) return ""
  const lower = url.toLowerCase()
  // Pass SVG through — already small, proxying just rasterizes.
  if (lower.endsWith(".svg") || lower.endsWith(".svg.png")) return url
  // Pass through anything that's already proxied (avoid double-wrap).
  if (url.startsWith(PROXY_BASE) || url.startsWith("/img/v1")) return url
  // Route through our Worker. encodeURIComponent handles all unsafe chars
  // (Worker decodes once on the server side).
  return `${PROXY_BASE}url=${encodeURIComponent(url)}&w=${widthPx}`
}

/**
 * Standard widths used across the app (DESIGN.md v3.0 §D.5).
 * Values picked to match real rendered sizes on a 1440px viewport with 2x DPR
 * margin. The proxy snaps each to the next Wikimedia thumb step (320, 480,
 * 640, 800, 1024, 1280, 1600, 2048) so we always hit their pre-cached tier.
 */
export const PHOTO_WIDTHS = {
  /** CharityCard 3:2 photo (3-col grid, ~430px wide @1440 viewport, 2x DPR = 860 → round to 800) */
  card: 800,
  /** HeroBucketCard full-bleed background (1/3 of viewport ≈ 480px @1440, 2x = 960 → 1024) */
  bucketHero: 1024,
  /** Detail-page hero photo (full-bleed @1440, 2x DPR = 2880 → cap at 1600 for sanity) */
  detailHero: 1600,
} as const
