/**
 * Image proxy / thumbnail helper.
 *
 * Wikimedia Commons recently locked down ad-hoc thumbnail requests
 * (`/wikipedia/commons/thumb/.../{N}px-Filename.jpg` returns HTTP 400 for any
 * size not pre-cached by their pipeline). Loading 19 full-size originals on
 * the catalog page brought page-weight to 50+ MB.
 *
 * v3.15.2 — strategy is now source-dependent:
 *   - Wikimedia originals: load **direct** (bypass weserv). weserv.nl is
 *     currently rate-limited by Wikimedia (returns 429 upstream → 404
 *     downstream); their thumb endpoint requires a server-side policy step
 *     we can't comply with from the browser. Loading the original adds
 *     page weight (~3-8 MB per image) but visibly works. lazy-loading on
 *     catalog cards + browser caching mitigates real-world cost. Defer
 *     a proper image-resize CDN (Cloudflare Worker or Cloudflare Images)
 *     to v3.16.
 *   - Everything else (Unsplash, charity-own CDNs, etc.): keep weserv
 *     resize+proxy — it works for these sources because their origins
 *     don't rate-limit the weserv IP and they advertise CORS headers.
 *
 * v3.15.1 — dropped `output=webp` because Chrome's Opaque Response Blocking
 * (ORB) silently rejects cross-origin webp from weserv when the source is
 * wikimedia.org. Together with `crossorigin="anonymous"` on `<img>` tags,
 * this addresses the ORB symptom — but the root weserv issue (Wikimedia
 * rate-limit) remained, hence v3.15.2.
 *
 * SVG: pass through unchanged (already small; weserv would rasterize).
 */

const WESERV_BASE = "https://images.weserv.nl/?"

export function wikimediaThumb(
  url: string | null | undefined,
  widthPx: number,
): string {
  if (!url) return ""
  const lower = url.toLowerCase()
  // Pass SVG through — already small, proxying just rasterizes.
  if (lower.endsWith(".svg") || lower.endsWith(".svg.png")) return url
  // Pass through anything that's already proxied (avoid double-wrap).
  if (url.startsWith(WESERV_BASE)) return url
  // v3.15.2 — bypass weserv for Wikimedia (weserv is rate-limited by upstream).
  // Wikimedia originals have correct CORS+CORP headers, so the browser loads
  // them directly without ORB or 404 issues. Cost: page weight.
  if (lower.includes("upload.wikimedia.org/")) return url
  // weserv expects the URL WITHOUT the protocol. It auto-detects http/https.
  let bare = url
  if (bare.startsWith("https://")) bare = bare.slice("https://".length)
  else if (bare.startsWith("http://")) bare = bare.slice("http://".length)
  // weserv decodes `url=` exactly once. Source URLs may already contain
  // percent-escapes (`%2C`, `%28`, etc.). URLSearchParams re-encodes `%` to
  // `%25`, double-encoding and breaking weserv. So escape only the characters
  // that would break the outer query string (`&`, `#`) and leave existing
  // percent-escapes intact.
  const safeBare = bare.replace(/&/g, "%26").replace(/#/g, "%23")
  const params = new URLSearchParams({
    w: String(widthPx),
    q: "80",
    // Cover-fit the requested width; prevents distortion. Default is "fit=inside".
    fit: "cover",
  })
  return `${WESERV_BASE}url=${safeBare}&${params.toString()}`
}

/**
 * Standard widths used across the app (DESIGN.md v3.0 §D.5).
 * Values picked to match real rendered sizes on a 1440px viewport with 2x DPR
 * margin. The proxy caches at edge, so distinct widths are cheap.
 */
export const PHOTO_WIDTHS = {
  /** CharityCard 3:2 photo (3-col grid, ~430px wide @1440 viewport, 2x DPR = 860 → round to 800) */
  card: 800,
  /** HeroBucketCard full-bleed background (1/3 of viewport ≈ 480px @1440, 2x = 960 → 1000) */
  bucketHero: 1000,
  /** Detail-page hero photo (full-bleed @1440, 2x DPR = 2880 → cap at 1600 for sanity) */
  detailHero: 1600,
} as const
