/**
 * trustgive-web Worker — v3.16.
 *
 * Two responsibilities:
 *   1. `/img/v1?url=...&w=N` — image proxy that fetches third-party origins
 *      with a compliant User-Agent, rewrites Wikimedia URLs to thumbnail
 *      endpoints, caches at Cloudflare edge for 30 days, and sets the headers
 *      Chrome needs to render the image cross-origin (CORS + CORP).
 *
 *      Replaces `images.weserv.nl` (dropped in v3.16 because (a) Chrome's ORB
 *      blocks weserv's WebP responses on Wikimedia sources, and (b) weserv
 *      never resized Wikimedia URLs — it just proxied originals, which was
 *      3-8 MB per hero photo).
 *
 *   2. Everything else → static assets via env.ASSETS.fetch(). SPA fallback
 *      to index.html for unknown routes (handled by wrangler `not_found_handling`).
 *
 * Why a Worker instead of weserv.nl: weserv doesn't comply with Wikimedia's
 * policy of "use a real User-Agent" and doesn't request the pre-cached
 * thumbnail URLs. Our Worker:
 *   - Sets `User-Agent: TrustGive/1.0 (https://trustgive.org; hello@trustgive.org)`
 *     — meets Wikimedia's UA-policy requirement.
 *   - Rewrites `/wikipedia/commons/{a}/{ab}/{filename}` to the
 *     `/wikipedia/commons/thumb/{a}/{ab}/{filename}/{N}px-{filename}` form
 *     which gives back pre-cached thumbnails at standard widths.
 *   - Snaps requested widths to the standard Wikimedia thumbnail steps
 *     (320, 480, 640, 800, 1024, 1280, 1600, 2048) so we hit their cache.
 *
 * Edge caching: Cloudflare's `caches.default` is keyed by full request URL.
 * Each (origin URL, width) pair becomes a separate cache entry. TTL 30 days.
 *
 * Failure modes handled:
 *   - Thumbnail 404 (e.g. SVG) → fall back to original URL.
 *   - Origin 404/5xx → return that status verbatim (transparent).
 *   - Missing `url` param → 400.
 *   - Non-image origin → returned anyway with CORP header (callers should
 *     only pass image URLs, but we don't sniff/validate to keep the Worker
 *     stateless).
 */

interface Env {
  ASSETS: Fetcher
}

const ALLOWED_WIDTHS = [320, 480, 640, 800, 1024, 1280, 1600, 2048] as const

/** Snap requested width up to the next standard Wikimedia thumb step. */
function normaliseWidth(requested: number): number {
  for (const w of ALLOWED_WIDTHS) {
    if (requested <= w) return w
  }
  return ALLOWED_WIDTHS[ALLOWED_WIDTHS.length - 1]
}

/**
 * Rewrite a Wikimedia Commons URL to the thumbnail endpoint at the given
 * width. Returns null for non-Wikimedia URLs.
 *
 * Input:
 *   https://upload.wikimedia.org/wikipedia/commons/6/67/Filename.jpg
 * Output (w=800):
 *   https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Filename.jpg/800px-Filename.jpg
 *
 * SVGs use a different filename pattern (`{N}px-Filename.svg.png`).
 */
function wikimediaThumbUrl(original: string, width: number): string | null {
  const match = original.match(
    /^https?:\/\/upload\.wikimedia\.org\/wikipedia\/commons\/([0-9a-f])\/([0-9a-f]{2})\/(.+)$/i,
  )
  if (!match) return null
  if (original.includes("/thumb/")) return null // already a thumb
  const [, a, ab, filename] = match
  const lower = filename.toLowerCase()
  const thumbName = lower.endsWith(".svg")
    ? `${width}px-${filename}.png`
    : `${width}px-${filename}`
  return `https://upload.wikimedia.org/wikipedia/commons/thumb/${a}/${ab}/${filename}/${thumbName}`
}

const UA_HEADER =
  "TrustGive/1.0 (+https://trustgive.org; contact: hello@trustgive.org)"

const FETCH_HEADERS: HeadersInit = {
  "User-Agent": UA_HEADER,
  Accept: "image/*,*/*;q=0.8",
  "Accept-Language": "en;q=0.9",
}

const RESPONSE_HEADERS = {
  "Cache-Control": "public, max-age=2592000, immutable",
  "Access-Control-Allow-Origin": "*",
  "Cross-Origin-Resource-Policy": "cross-origin",
  "Timing-Allow-Origin": "*",
  Vary: "Accept",
}

function withProxyHeaders(upstream: Response, extra: Record<string, string> = {}): Response {
  const headers = new Headers(upstream.headers)
  for (const [k, v] of Object.entries(RESPONSE_HEADERS)) headers.set(k, v)
  for (const [k, v] of Object.entries(extra)) headers.set(k, v)
  // Drop headers that confuse the browser when we re-emit them.
  headers.delete("Content-Security-Policy")
  headers.delete("Set-Cookie")
  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers,
  })
}

async function handleImageProxy(request: Request): Promise<Response> {
  const url = new URL(request.url)
  const target = url.searchParams.get("url")
  const widthParam = url.searchParams.get("w") || "1024"

  if (!target) {
    return new Response("Missing `url` parameter.", { status: 400 })
  }

  let parsedTarget: URL
  try {
    parsedTarget = new URL(target.startsWith("http") ? target : `https://${target}`)
  } catch {
    return new Response("Invalid `url` parameter.", { status: 400 })
  }

  // Only allow http(s) origins. Refuse file:/data:/javascript:/etc.
  if (parsedTarget.protocol !== "http:" && parsedTarget.protocol !== "https:") {
    return new Response("Only http(s) origins allowed.", { status: 400 })
  }

  const width = normaliseWidth(parseInt(widthParam, 10) || 1024)

  // Edge cache key: (target URL, normalised width). Width matters because the
  // same origin URL at different widths is a different image.
  const cacheKey = new Request(
    `https://img-cache.trustgive.org/?u=${encodeURIComponent(parsedTarget.toString())}&w=${width}`,
    { method: "GET" },
  )
  const cache = (caches as unknown as { default: Cache }).default
  const cached = await cache.match(cacheKey)
  if (cached) {
    const headers = new Headers(cached.headers)
    headers.set("X-Cache", "HIT")
    return new Response(cached.body, { status: cached.status, headers })
  }

  // Try thumbnail endpoint first for Wikimedia; fall back to original.
  const thumbUrl = wikimediaThumbUrl(parsedTarget.toString(), width)
  const attempts: string[] = []
  if (thumbUrl) attempts.push(thumbUrl)
  attempts.push(parsedTarget.toString())

  let upstream: Response | null = null
  let attempted = ""
  for (const candidate of attempts) {
    attempted = candidate
    try {
      const r = await fetch(candidate, {
        method: "GET",
        headers: FETCH_HEADERS,
        redirect: "follow",
        cf: {
          cacheTtl: 60 * 60 * 24 * 30, // 30 days
          cacheEverything: true,
        },
      } as RequestInit)
      if (r.ok) {
        upstream = r
        break
      }
      // If thumb 404'd, try the original. Otherwise (e.g. 5xx) bail.
      if (r.status === 404 && candidate === thumbUrl) {
        continue
      }
      upstream = r
      break
    } catch {
      // Network error fetching one candidate — try next.
      continue
    }
  }

  if (!upstream) {
    return new Response(`Upstream unreachable: ${attempted}`, { status: 502 })
  }

  const finalResponse = withProxyHeaders(upstream, {
    "X-Cache": "MISS",
    "X-Source": attempted,
    "X-Width": String(width),
  })

  // Cache successful responses only; don't pollute the cache with 4xx/5xx.
  if (finalResponse.ok) {
    const toCache = finalResponse.clone()
    // The cache copy doesn't need the X-Cache: MISS — strip it.
    const cacheHeaders = new Headers(toCache.headers)
    cacheHeaders.delete("X-Cache")
    const cacheBody = await toCache.arrayBuffer()
    await cache.put(
      cacheKey,
      new Response(cacheBody, { status: toCache.status, headers: cacheHeaders }),
    )
  }

  return finalResponse
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)

    if (url.pathname === "/img/v1") {
      // Image proxy. Only GET is allowed (and HEAD by convention).
      if (request.method !== "GET" && request.method !== "HEAD") {
        return new Response("Method not allowed.", {
          status: 405,
          headers: { Allow: "GET, HEAD" },
        })
      }
      return handleImageProxy(request)
    }

    // Everything else — defer to the static assets binding.
    return env.ASSETS.fetch(request)
  },
} satisfies ExportedHandler<Env>
