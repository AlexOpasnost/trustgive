/**
 * Image proxy / thumbnail helper.
 *
 * Wikimedia Commons recently locked down ad-hoc thumbnail requests
 * (`/wikipedia/commons/thumb/.../{N}px-Filename.jpg` returns HTTP 400 for any
 * size not pre-cached by their pipeline). Loading 19 full-size originals on
 * the catalog page brought page-weight to 50+ MB.
 *
 * Solution: route all third-party images through `images.weserv.nl`, a free
 * image proxy/CDN used widely in OSS (no API key, no rate limits at our scale,
 * caches at edge).
 *
 * v3.15: dropped `output=webp` — Chrome's Opaque Response Blocking (ORB)
 * silently rejects cross-origin webp responses from weserv when the source
 * is wikimedia.org, breaking ~80% of detail-page heroes. Letting weserv
 * default to the source mime (JPEG/PNG) bypasses ORB at a ~30% bytes cost,
 * still ~95% smaller than the un-proxied original because of `w=` resize.
 *
 * Result on a typical 6.7 MB Wikimedia JPEG (JPEG output, q=80):
 *   - w=600 → ~55 KB (99% reduction)
 *   - w=800 → ~80 KB
 *   - w=1200 → ~140 KB
 *
 * For non-Wikimedia URLs (e.g. our own future R2 bucket), the proxy still
 * works since weserv accepts any public URL.
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
  // weserv expects the URL WITHOUT the protocol. It auto-detects http/https.
  let bare = url
  if (bare.startsWith("https://")) bare = bare.slice("https://".length)
  else if (bare.startsWith("http://")) bare = bare.slice("http://".length)
  // weserv accepts the URL as a query param. URL-encode the whole bare URL so
  // any embedded `&` / `?` / spaces don't break the outer query string.
  const params = new URLSearchParams({
    url: bare,
    w: String(widthPx),
    q: "80",
    // Cover-fit the requested width; prevents distortion. Default is "fit=inside".
    fit: "cover",
    // No `output=` — let weserv echo the source mime (JPEG for Wikimedia).
    // `output=webp` triggers Chrome ORB on Wikimedia sources at large widths.
  })
  return `${WESERV_BASE}${params.toString()}`
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
