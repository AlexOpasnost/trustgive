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
 * v3.17 — build a `srcset` string so the browser picks the right width for
 * the device. The Worker snaps each width to a Wikimedia thumb tier, so we
 * pass the tiers directly. Returns "" for falsy/SVG URLs (the caller should
 * fall back to a plain `src` in that case).
 *
 * Pair with a `sizes` attribute that describes how wide the image actually
 * renders — without `sizes` the browser assumes 100vw and over-fetches.
 */
export function buildSrcSet(
  url: string | null | undefined,
  widths: readonly number[],
): string {
  if (!url) return ""
  const lower = url.toLowerCase()
  if (lower.endsWith(".svg") || lower.endsWith(".svg.png")) return ""
  return widths
    .map((w) => `${wikimediaThumb(url, w)} ${w}w`)
    .join(", ")
}

/**
 * srcset width tiers per render context. Every value is a Wikimedia-allowed
 * width: the 2024 thumbnail restriction (w.wiki/GHai) only generates a fixed
 * set — [120, 250, 500, 960, 1280, 1920] — and 400s anything else. This is
 * mirrored in worker/index.ts `ALLOWED_WIDTHS`; keep the two in sync.
 *
 * The `sizes` attribute (set per-component) tells the browser which tier to
 * actually fetch.
 */
export const SRCSET_WIDTHS = {
  /** CharityCard 3:2 photo — full-width on mobile (~400) → ~430px in the 3-col grid. */
  card: [250, 500, 960],
  /** HeroBucketCard — full-bleed on mobile, ~1/3 viewport on desktop. */
  bucketHero: [500, 960, 1280],
  /** Detail-page hero — always full-bleed. */
  detailHero: [960, 1280, 1920],
} as const

/**
 * Single-width fallback for the plain `src` attribute — the tier closest to
 * the real rendered size on a 1440px viewport at ~2x DPR. Every value is a
 * Wikimedia-allowed width (see SRCSET_WIDTHS note).
 */
export const PHOTO_WIDTHS = {
  /** CharityCard 3:2 photo (3-col grid ≈ 430px @1440, 2x ≈ 860 → 960 tier). */
  card: 960,
  /** HeroBucketCard full-bleed (≈ 1/3 viewport ≈ 480px @1440, 2x ≈ 960). */
  bucketHero: 960,
  /** Detail-page hero (full-bleed @1440, 2x ≈ 2880 → cap at 1280 for sanity). */
  detailHero: 1280,
} as const
