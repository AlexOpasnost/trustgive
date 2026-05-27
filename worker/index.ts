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

/**
 * Wikimedia's allowed on-demand thumbnail widths.
 *
 * As of the 2024 thumbnail restriction (w.wiki/GHai) Wikimedia only generates
 * thumbnails at a fixed allowlist of widths; any other width returns HTTP 400.
 * This exact set was found empirically (every other width in a 35-width sweep
 * returned 400, and the set held across multiple test images):
 *
 *   - 400 = width not on the allowlist
 *   - 404 = allowed width but ≥ the original's width (can't upscale) → the
 *           proxy falls back to the original URL
 *   - 200 = allowed, ≤ original, generated
 */
const ALLOWED_WIDTHS = [120, 250, 500, 960, 1280, 1920] as const

/** Snap requested width up to the next allowed Wikimedia thumb step. */
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
  "Access-Control-Allow-Origin": "*",
  "Cross-Origin-Resource-Policy": "cross-origin",
  "Timing-Allow-Origin": "*",
  Vary: "Accept",
}

function withProxyHeaders(upstream: Response, extra: Record<string, string> = {}): Response {
  const headers = new Headers(upstream.headers)
  for (const [k, v] of Object.entries(RESPONSE_HEADERS)) headers.set(k, v)
  // Cache-Control is status-dependent: a 30-day immutable cache for the image
  // itself, but `no-store` for any error so the CF edge never pins a 4xx/5xx
  // (an earlier bug cached Wikimedia 400s for 30 days).
  headers.set(
    "Cache-Control",
    upstream.ok ? "public, max-age=2592000, immutable" : "no-store",
  )
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
          // Per-status TTL: pin 2xx for 30 days, never pin 4xx/5xx (an
          // earlier bug cached Wikimedia 400s).
          cacheTtlByStatus: {
            "200-299": 60 * 60 * 24 * 30,
            "400-499": 0,
            "500-599": 0,
          },
          cacheEverything: true,
        },
      } as RequestInit)
      if (r.ok) {
        upstream = r
        break
      }
      // Thumb endpoint failed — fall back to the original URL. Wikimedia
      // returns 404 when the allowed width is ≥ the original (can't upscale)
      // and 400 if the width somehow isn't on the allowlist; in both cases
      // the un-resized original still works. Only the original-URL attempt
      // (or a non-thumb 5xx) is allowed to become the final response.
      if (candidate === thumbUrl && (r.status === 404 || r.status === 400)) {
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

/**
 * `/sitemap.xml` — generated on the fly from the live API.
 *
 * A SPA can't ship a static sitemap that stays accurate as the catalog grows
 * (it's at 541 charities and climbing). So the Worker fetches every slug from
 * the API and emits a fresh sitemap, cached at the edge for 6 hours.
 *
 * Static routes (/, /charities, /methodology) get priority 0.8-1.0; charity
 * detail pages get 0.6. lastmod is omitted — the API summary doesn't carry a
 * per-charity updated_at, and a wrong lastmod is worse than none.
 */
async function handleSitemap(): Promise<Response> {
  const cache = (caches as unknown as { default: Cache }).default
  const cacheKey = new Request("https://trustgive.org/sitemap.xml")
  const cached = await cache.match(cacheKey)
  if (cached) return cached

  const base = "https://trustgive.org"
  const staticUrls = [
    { loc: `${base}/`, priority: "1.0" },
    { loc: `${base}/charities`, priority: "0.9" },
    { loc: `${base}/methodology`, priority: "0.8" },
  ]

  // Pull all slugs. The API caps page_size at 500 server-side, so we page
  // through with `next` until exhausted (catalog is 541 and climbing). Cap at
  // 5 pages (2500 charities) as a safety stop against a pagination bug.
  const slugs: string[] = []
  try {
    let nextUrl: string | null =
      "https://api.trustgive.org/api/charities/?page_size=500&sort=alphabetical"
    let guard = 0
    while (nextUrl && guard < 5) {
      guard += 1
      const res: Response = await fetch(nextUrl, {
        headers: { Accept: "application/json" },
        cf: { cacheTtl: 3600 },
      } as RequestInit)
      if (!res.ok) break
      const data = (await res.json()) as {
        results?: Array<{ slug: string }>
        next?: string | null
      }
      for (const c of data.results ?? []) {
        if (c.slug) slugs.push(c.slug)
      }
      nextUrl = data.next ?? null
    }
  } catch {
    // If the API is down we still emit the static-route sitemap rather than 500.
  }

  const xmlEscape = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")

  const entries = [
    ...staticUrls.map(
      (u) => `  <url><loc>${xmlEscape(u.loc)}</loc><priority>${u.priority}</priority></url>`,
    ),
    ...slugs.map(
      (slug) =>
        `  <url><loc>${xmlEscape(`${base}/charities/${slug}`)}</loc><priority>0.6</priority></url>`,
    ),
  ]

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries.join("\n")}
</urlset>
`

  const response = new Response(xml, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, max-age=21600", // 6h
    },
  })
  await cache.put(cacheKey, response.clone())
  return response
}

/**
 * Per-charity SEO/social meta injection for `/charities/{slug}`.
 *
 * The frontend is a client-rendered SPA, so every charity detail URL ships the
 * same static `<head>` from index.html: one generic title, one description, no
 * og:image. Two consequences this fixes:
 *   1. Social crawlers (LinkedIn, Twitter, Telegram, Facebook) read og:* from
 *      raw HTML and never run JS, so every shared charity link previewed as the
 *      generic homepage card with no image.
 *   2. Google sees 541 detail pages with duplicate descriptions and no
 *      structured data — weaker ranking, no rich results.
 *
 * This handler fetches the SPA shell from ASSETS and the charity record from
 * the API, then uses HTMLRewriter to rewrite the existing title/description/og
 * tags and append canonical + twitter + JSON-LD (schema.org NGO). The SPA still
 * hydrates and renders normally — we only enrich the `<head>` the crawler sees.
 *
 * Failure-safe: any API error or 404 falls through to the untouched SPA shell,
 * so a flaky API can never blank the page. Successful renders are edge-cached
 * for 1h, keyed by the canonical URL; failures are never cached (v3.16 lesson).
 */

const API_BASE = "https://api.trustgive.org"
const SITE_BASE = "https://trustgive.org"
const COUNTRY_LABEL: Record<string, string> = { US: "US", UK: "UK", RU: "Russian" }

interface LocalisedText {
  en?: string
  ru?: string
}
interface CharityDetail {
  slug: string
  name: LocalisedText
  tagline?: LocalisedText
  description?: LocalisedText
  logo_url?: string | null
  hero_photo_url?: string | null
  country?: string
  registration_id?: string
  founded_year?: number | null
  verification_status?: string
  donation_url?: string
  source_documents?: Array<{ url?: string; source_label?: string; label?: LocalisedText }>
}

function escapeAttr(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
}

/** Truncate to a clean length at a word boundary, with an ellipsis. */
function clamp(s: string, max: number): string {
  const flat = s.replace(/\s+/g, " ").trim()
  if (flat.length <= max) return flat
  const cut = flat.slice(0, max - 1)
  const lastSpace = cut.lastIndexOf(" ")
  return (lastSpace > max * 0.6 ? cut.slice(0, lastSpace) : cut).trimEnd() + "…"
}

/** og:image routes through our own proxy so Wikimedia (UA-gated) images and
 * any origin are reliably fetchable by social crawlers at a fixed width. */
function ogImageUrl(photo: string): string {
  return `${SITE_BASE}/img/v1?url=${encodeURIComponent(photo)}&w=1280`
}

function buildJsonLd(c: CharityDetail, name: string, description: string, canonical: string): string {
  const ld: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "NGO",
    name,
    url: canonical,
    description,
  }
  if (c.logo_url) ld.logo = c.logo_url
  if (c.hero_photo_url) ld.image = c.hero_photo_url
  if (c.founded_year) ld.foundingDate = String(c.founded_year)
  if (c.country && COUNTRY_LABEL[c.country]) ld.areaServed = COUNTRY_LABEL[c.country]
  if (c.registration_id) ld.taxID = c.registration_id
  if (c.donation_url) {
    ld.potentialAction = { "@type": "DonateAction", target: c.donation_url }
  }
  const docs = (c.source_documents ?? []).filter((d) => d.url)
  if (docs.length) {
    ld.subjectOf = docs.map((d) => ({
      "@type": "CreativeWork",
      name: d.source_label || d.label?.en || "Source document",
      url: d.url,
    }))
  }
  // Escape `<` so a stray "</script>" in any string can't break out of the tag.
  return JSON.stringify(ld).replace(/</g, "\\u003c")
}

async function handleCharityMeta(request: Request, env: Env, slug: string): Promise<Response> {
  const canonical = `${SITE_BASE}/charities/${slug}`
  const cache = (caches as unknown as { default: Cache }).default
  const cacheKey = new Request(canonical)
  const cached = await cache.match(cacheKey)
  if (cached) return cached

  // Always have the SPA shell ready — it's our fallback on any failure.
  const shell = await env.ASSETS.fetch(request)

  let charity: CharityDetail | null = null
  try {
    const res = await fetch(`${API_BASE}/api/charities/${encodeURIComponent(slug)}/`, {
      headers: { Accept: "application/json" },
      cf: { cacheTtl: 3600 } as RequestInit["cf"],
    })
    if (res.ok) charity = (await res.json()) as CharityDetail
  } catch {
    // API unreachable — fall through to the untouched shell.
  }

  if (!charity || !charity.name) return shell // 404 or API down → plain SPA

  const name = charity.name.en || charity.name.ru || slug
  const countryLabel = (charity.country && COUNTRY_LABEL[charity.country]) || ""
  const title = `${name} — ${countryLabel ? countryLabel + " " : ""}charity profile · TrustGive`
  const rawDesc =
    charity.description?.en || charity.tagline?.en || `${name} — verified charity profile on TrustGive.`
  const description = clamp(rawDesc, 160)
  const photo = charity.hero_photo_url || charity.logo_url || ""
  const ogImage = photo ? ogImageUrl(photo) : ""
  const jsonLd = buildJsonLd(charity, name, description, canonical)

  // Tags appended to <head>: canonical, the og:image we never had, twitter
  // card, and the JSON-LD block. Existing title/description/og:title/
  // og:description are rewritten in place below.
  const headExtras =
    `<link rel="canonical" href="${escapeAttr(canonical)}">` +
    `<meta property="og:url" content="${escapeAttr(canonical)}">` +
    (ogImage ? `<meta property="og:image" content="${escapeAttr(ogImage)}">` : "") +
    `<meta name="twitter:title" content="${escapeAttr(title)}">` +
    `<meta name="twitter:description" content="${escapeAttr(description)}">` +
    (ogImage ? `<meta name="twitter:image" content="${escapeAttr(ogImage)}">` : "") +
    `<script type="application/ld+json">${jsonLd}</script>`

  const rewriter = new HTMLRewriter()
    .on("title", {
      element(el) {
        el.setInnerContent(title)
      },
    })
    .on('meta[name="description"]', {
      element(el) {
        el.setAttribute("content", description)
      },
    })
    .on('meta[property="og:title"]', {
      element(el) {
        el.setAttribute("content", title)
      },
    })
    .on('meta[property="og:description"]', {
      element(el) {
        el.setAttribute("content", description)
      },
    })
    .on('meta[property="og:type"]', {
      element(el) {
        el.setAttribute("content", "profile")
      },
    })
    .on("head", {
      element(el) {
        el.append(headExtras, { html: true })
      },
    })

  // Buffer the rewritten HTML so we can both return and cache it. index.html is
  // small; streaming isn't worth the complexity here.
  const transformed = rewriter.transform(shell)
  const html = await transformed.text()
  const response = new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      // Browser revalidates; edge holds 1h. Charity data changes rarely and the
      // sitemap already drives crawl freshness.
      "Cache-Control": "public, max-age=0, s-maxage=3600, must-revalidate",
    },
  })
  await cache.put(cacheKey, response.clone())
  return response
}

const CHARITY_DETAIL = /^\/charities\/([^/]+)\/?$/

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

    if (url.pathname === "/sitemap.xml") {
      return handleSitemap()
    }

    // Charity detail pages (`/charities/{slug}`, GET only) get per-charity
    // <head> meta + JSON-LD injected at the edge. `/charities` (the catalog)
    // and asset paths don't match and fall through to the SPA shell.
    const detailMatch = request.method === "GET" && CHARITY_DETAIL.exec(url.pathname)
    if (detailMatch) {
      return handleCharityMeta(request, env, decodeURIComponent(detailMatch[1]))
    }

    // Everything else — defer to the static assets binding.
    return env.ASSETS.fetch(request)
  },
} satisfies ExportedHandler<Env>
