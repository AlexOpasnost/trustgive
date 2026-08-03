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
 *
 * SITEMAP_VERSION is part of the edge-cache key, and must be bumped whenever the
 * *shape* of the sitemap changes. `caches.default` survives a deploy: after
 * v3.21 shipped, the edge kept serving the previous 743-URL body — with none of
 * the new hub or pagination URLs — because the key was a bare constant and the
 * entry still had hours to live. A sitemap that silently outlives the deploy
 * that changed it is the same failure this project has been bitten by three
 * times: everything reports success while production serves the old thing.
 * Charity-count changes need no bump; the 6-hour TTL handles those.
 */
// v3.22: added /api. The first v3.22 deploy shipped without bumping this and
// the edge kept serving the 810-URL body for hours — the very failure the
// paragraph above describes, repeated by the person who wrote it.
const SITEMAP_VERSION = "v3.24"

/**
 * Published research slugs, mirroring frontend/web/src/content/research.ts.
 *
 * Duplicated rather than imported because the Worker and the SPA are separate
 * bundles with no shared module. Two entries is cheap to keep in step; if this
 * list grows, move it behind an API endpoint the way hubs and stats are.
 */
const RESEARCH_SLUGS = [
  "how-old-is-charity-financial-data",
  "what-we-could-not-verify",
] as const

async function handleSitemap(): Promise<Response> {
  const cache = (caches as unknown as { default: Cache }).default
  const cacheKey = new Request(`https://trustgive.org/sitemap.xml?v=${SITEMAP_VERSION}`)
  const cached = await cache.match(cacheKey)
  if (cached) return cached

  const base = "https://trustgive.org"
  const staticUrls = [
    { loc: `${base}/`, priority: "1.0" },
    { loc: `${base}/charities`, priority: "0.9" },
    { loc: `${base}/methodology`, priority: "0.8" },
    { loc: `${base}/data-sources`, priority: "0.7" },
    { loc: `${base}/about`, priority: "0.6" },
    { loc: `${base}/api`, priority: "0.6" },
    { loc: `${base}/research`, priority: "0.8" },
    // Research pieces are listed individually: each is a standalone document
    // that someone might cite, and the index alone would leave them one hop
    // further from the crawler than they deserve. Kept in step with
    // frontend/web/src/content/research.ts.
    ...RESEARCH_SLUGS.map((slug) => ({
      loc: `${base}/research/${slug}`,
      priority: "0.7",
    })),
  ]

  // Pull all slugs. The API caps page_size at 500 server-side, so we page
  // through with `next` until exhausted (catalog is 541 and climbing). Cap at
  // 5 pages (2500 charities) as a safety stop against a pagination bug.
  const slugs: string[] = []
  let catalogueCount = 0
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
        count?: number
        results?: Array<{ slug: string }>
        next?: string | null
      }
      if (guard === 1) catalogueCount = data.count ?? 0
      for (const c of data.results ?? []) {
        if (c.slug) slugs.push(c.slug)
      }
      nextUrl = data.next ?? null
    }
  } catch {
    // If the API is down we still emit the static-route sitemap rather than 500.
  }

  // v3.21 — hub sections and the paginated catalogue. Listing these matters more
  // than listing the charity pages did: a sitemap entry for a page that nothing
  // links to gets discovered and then ignored, which is the state 640 URLs were
  // in. These are pages the catalogue actually links to, so the sitemap is
  // telling Google about a graph it can also walk.
  const hubs = await fetchHubIndex()
  const hubUrls: string[] = []
  if (hubs) {
    for (const hub of [...hubs.registries, ...hubs.countries, ...hubs.causes]) {
      const pages = totalPages(hub.count)
      for (let p = 1; p <= pages; p += 1) {
        hubUrls.push(`${base}${pageHref(hub.path, p)}`)
      }
    }
  }

  const cataloguePageUrls: string[] = []
  for (let p = 2; p <= totalPages(catalogueCount); p += 1) {
    cataloguePageUrls.push(`${base}/charities?page=${p}`)
  }

  const xmlEscape = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")

  const entries = [
    ...staticUrls.map(
      (u) => `  <url><loc>${xmlEscape(u.loc)}</loc><priority>${u.priority}</priority></url>`,
    ),
    // Hubs rank above individual profiles: they are the pages that distribute
    // crawl attention to the 370 charity pages below them.
    ...hubUrls.map(
      (loc) => `  <url><loc>${xmlEscape(loc)}</loc><priority>0.7</priority></url>`,
    ),
    ...cataloguePageUrls.map(
      (loc) => `  <url><loc>${xmlEscape(loc)}</loc><priority>0.7</priority></url>`,
    ),
    ...slugs.map(
      (slug) =>
        `  <url><loc>${xmlEscape(`${base}/charities/${slug}`)}</loc><priority>0.6</priority></url>`,
    ),
    // "Is X legitimate?" landing pages (v3.19). Lower priority than the profile
    // itself — they target a specific long-tail query rather than the canonical
    // charity record.
    ...slugs.map(
      (slug) =>
        `  <url><loc>${xmlEscape(`${base}/charities/${slug}/legit`)}</loc><priority>0.5</priority></url>`,
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

  // Always have the SPA shell ready — it's our fallback on any failure — and
  // read it before the cache lookup, because its build token keys the cache
  // (see fetchShell: `caches.default` outlives a deploy).
  const { html: shell, version } = await fetchShell(request, env)

  const cache = (caches as unknown as { default: Cache }).default
  const cacheKey = new Request(`${canonical}?v=${version}`)
  const cached = await cache.match(cacheKey)
  if (cached) return cached

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

  if (!charity || !charity.name) return plainShell(shell) // 404 or API down → plain SPA

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
  const transformed = rewriter.transform(plainShell(shell))
  const html = await transformed.text()
  const response = new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": HTML_CACHE_CONTROL,
    },
  })
  await cache.put(cacheKey, response.clone())
  return response
}

/**
 * Per-charity "Is X legitimate?" landing page meta for `/charities/{slug}/legit`.
 *
 * Same edge-render strategy as handleCharityMeta, but the payload comes from the
 * SEO endpoint (apps/seo) — which already frames the charity as a question +
 * verdict + evidence — and the structured data is a schema.org **FAQPage**. That
 * FAQPage is the point: it makes the page eligible for the "People also ask" /
 * rich-result answer box on queries like "is {name} a legitimate charity", which
 * the plain NGO profile can't win. og:type is `article` (a Q&A page, not a
 * profile). Failure-safe: any API error falls through to the untouched SPA shell.
 */
interface SeoPayload {
  h1?: string
  answer?: string
  evidence_summary?: LocalisedText
  meta?: { title?: string; description?: string }
  charity?: CharityDetail
}

async function handleLegitMeta(request: Request, env: Env, slug: string): Promise<Response> {
  const canonical = `${SITE_BASE}/charities/${slug}/legit`

  const { html: shell, version } = await fetchShell(request, env)

  const cache = (caches as unknown as { default: Cache }).default
  const cacheKey = new Request(`${canonical}?v=${version}`)
  const cached = await cache.match(cacheKey)
  if (cached) return cached

  let payload: SeoPayload | null = null
  try {
    const res = await fetch(`${API_BASE}/api/seo/charities/${encodeURIComponent(slug)}/?lang=en`, {
      headers: { Accept: "application/json" },
      cf: { cacheTtl: 3600 } as RequestInit["cf"],
    })
    if (res.ok) payload = (await res.json()) as SeoPayload
  } catch {
    // API unreachable — fall through to the untouched shell.
  }

  if (!payload || !payload.h1) return plainShell(shell) // 404 or API down → plain SPA

  const question = payload.h1
  const evidence = payload.evidence_summary?.en ?? ""
  const answerText = clamp(`${payload.answer ?? ""} ${evidence}`.trim(), 500)
  const title = payload.meta?.title || `${question} · TrustGive`
  const description = clamp(`${payload.answer ?? ""} ${evidence}`.trim(), 160)
  const photo = payload.charity?.hero_photo_url || payload.charity?.logo_url || ""
  const ogImage = photo ? ogImageUrl(photo) : ""

  const faqLd = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: [
      {
        "@type": "Question",
        name: question,
        acceptedAnswer: { "@type": "Answer", text: answerText },
      },
    ],
  }).replace(/</g, "\\u003c")

  const headExtras =
    `<link rel="canonical" href="${escapeAttr(canonical)}">` +
    `<meta property="og:url" content="${escapeAttr(canonical)}">` +
    (ogImage ? `<meta property="og:image" content="${escapeAttr(ogImage)}">` : "") +
    `<meta name="twitter:title" content="${escapeAttr(title)}">` +
    `<meta name="twitter:description" content="${escapeAttr(description)}">` +
    (ogImage ? `<meta name="twitter:image" content="${escapeAttr(ogImage)}">` : "") +
    `<script type="application/ld+json">${faqLd}</script>`

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
        el.setAttribute("content", "article")
      },
    })
    .on("head", {
      element(el) {
        el.append(headExtras, { html: true })
      },
    })

  const transformed = rewriter.transform(plainShell(shell))
  const html = await transformed.text()
  const response = new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": HTML_CACHE_CONTROL,
    },
  })
  await cache.put(cacheKey, response.clone())
  return response
}

/* -------------------------------------------------------------------------- *
 * Crawlable catalogue: hub pages + paginated catalogue (v3.21)
 *
 * The problem this solves, from Search Console on 2026-07-31: 640 URLs sitting
 * in "Discovered — currently not indexed". Google knew every charity URL from
 * the sitemap and crawled almost none of them. A sitemap entry is a hint, not
 * a vote — importance comes from links, and the catalogue had none pointing at
 * charities 61–370 because they lived behind a "Load more" button.
 *
 * Two fixes ship together:
 *   - the SPA now renders `?page=N` links and hub sections (country / cause /
 *     registry), so the link graph exists;
 *   - and this Worker renders that same graph into the HTML the crawler
 *     receives, so it does not depend on a render pass that Google defers for
 *     exactly the low-priority pages we're trying to promote.
 *
 * The injected markup goes inside `<div id="root">`. React's `createRoot()`
 * clears the container on its first render, so the SPA replaces it a few hundred
 * milliseconds later with the identical content, properly styled. It is not
 * cloaking: the crawler is served the same links, headings and counts a visitor
 * sees.
 * -------------------------------------------------------------------------- */

/** Must match CATALOG_PAGE_SIZE in the SPA (components/catalog/CatalogResults). */
const CATALOG_PAGE_SIZE = 60

/**
 * The SPA shell plus a token identifying the build it belongs to.
 *
 * Every handler here caches a rewritten copy of `index.html` at the edge for an
 * hour, and `caches.default` **survives a deploy** — so without a per-build
 * token those cached copies keep pointing at the previous JS bundle after the
 * next release. Users get a working-but-stale app, and, worse, the one check
 * this project relies on to prove a deploy landed ("does the live HTML name the
 * bundle I just built?") starts answering for a page that was cached before the
 * deploy. That is the exact shape of the failure this codebase has hit three
 * times: everything reports success while production serves the old thing.
 *
 * The token is the hashed bundle filename Vite already emits, so it changes on
 * its own with every build — nothing to remember to bump.
 *
 * The body is returned as a string rather than a Response because a Response
 * body can only be read once, and we need it both to derive the token and to
 * feed HTMLRewriter.
 */
async function fetchShell(
  request: Request,
  env: Env,
): Promise<{ html: string; version: string }> {
  const html = await (await env.ASSETS.fetch(request)).text()
  const match = html.match(/\/assets\/(index-[A-Za-z0-9_-]+)\.js/)
  return { html, version: match ? match[1] : "unknown" }
}

/**
 * Cache-Control for every HTML page this Worker renders.
 *
 * Was `s-maxage=3600`. That hour is charged twice on a deploy: Cloudflare's CDN
 * caches the response by URL *in front of* the Worker, so a page requested
 * before a release keeps being served from the edge without the Worker running
 * at all — the per-build cache key in fetchShell can't help, because the Worker
 * is never reached. Observed directly after the v3.21 deploy: `/charities?page=3`
 * (never requested before) came back on the new bundle while `/charities` (which
 * had been) stayed on the old one.
 *
 * With no `purge_cache` permission on the deploy token, the only lever is the
 * TTL. Five minutes bounds post-release staleness to something a person can wait
 * out, and `stale-while-revalidate` keeps the page fast meanwhile: the edge
 * serves the old copy instantly and refreshes it in the background. Regenerating
 * costs two API subrequests, both themselves edge-cached via `cf.cacheTtl`.
 */
const HTML_CACHE_CONTROL =
  "public, max-age=0, s-maxage=300, stale-while-revalidate=3600, must-revalidate"

/** The untouched shell, for every path where we decline to enrich the page. */
function plainShell(html: string): Response {
  return new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "public, max-age=0, must-revalidate",
    },
  })
}

interface HubItem {
  kind: "country" | "cause" | "registry"
  slug: string
  label: LocalisedText
  count: number
  path: string
  code?: string
  publisher?: string
  host?: string
  country?: string
  description?: LocalisedText
}

interface HubIndex {
  min_size: number
  countries: HubItem[]
  causes: HubItem[]
  registries: HubItem[]
}

interface CharityPage {
  count: number
  results: Array<{ slug: string; name?: LocalisedText; tagline?: LocalisedText; country?: string }>
}

async function fetchHubIndex(): Promise<HubIndex | null> {
  try {
    const res = await fetch(`${API_BASE}/api/hubs/`, {
      headers: { Accept: "application/json" },
      cf: { cacheTtl: 3600 } as RequestInit["cf"],
    })
    if (!res.ok) return null
    return (await res.json()) as HubIndex
  } catch {
    return null
  }
}

interface CatalogueStats {
  charities?: number
  countries?: number
  last_checked?: string | null
}

/** Catalogue counts. Shared by the homepage meta and the Dataset markup so the
 *  two can never state different sizes for the same catalogue. */
async function fetchStats(): Promise<CatalogueStats | null> {
  try {
    const res = await fetch(`${API_BASE}/api/stats/`, {
      headers: { Accept: "application/json" },
      cf: { cacheTtl: 3600 } as RequestInit["cf"],
    })
    if (!res.ok) return null
    return (await res.json()) as CatalogueStats
  } catch {
    return null
  }
}

async function fetchCharityPage(query: string): Promise<CharityPage | null> {
  try {
    const res = await fetch(`${API_BASE}/api/charities/?${query}`, {
      headers: { Accept: "application/json" },
      cf: { cacheTtl: 600 } as RequestInit["cf"],
    })
    if (!res.ok) return null
    return (await res.json()) as CharityPage
  } catch {
    return null
  }
}

/** API query string selecting exactly the charities a hub claims to hold. */
function hubApiQuery(hub: HubItem, page: number): string {
  const params = new URLSearchParams({
    sort: "alphabetical",
    page: String(page),
    page_size: String(CATALOG_PAGE_SIZE),
  })
  if (hub.kind === "country") params.set("country", hub.code ?? "")
  else if (hub.kind === "cause") params.set("cause", hub.slug)
  else params.set("registry", hub.slug)
  return params.toString()
}

function totalPages(count: number): number {
  return Math.max(1, Math.ceil(count / CATALOG_PAGE_SIZE))
}

/** `path` with `?page=n`; page 1 keeps the bare path so it has a single URL. */
function pageHref(path: string, page: number, extra = ""): string {
  const qs = [extra, page > 1 ? `page=${page}` : ""].filter(Boolean).join("&")
  return qs ? `${path}?${qs}` : path
}

/**
 * The crawlable body: heading, intro, one link per charity, the page links, and
 * the hub directory. Deliberately plain — it exists for a parser, and it is on
 * screen only until React mounts.
 */
function crawlBody(opts: {
  heading: string
  intro: string
  charities: Array<{ slug: string; name: string; tagline: string }>
  pages: Array<{ href: string; label: string; current: boolean }>
  directory: HubItem[]
  activePath?: string
}): string {
  const items = opts.charities
    .map(
      (c) =>
        `<li><a href="/charities/${escapeAttr(c.slug)}">${escapeAttr(c.name)}</a>` +
        (c.tagline ? ` — ${escapeAttr(c.tagline)}` : "") +
        `</li>`,
    )
    .join("")

  const pageLinks = opts.pages
    .map((p) =>
      p.current
        ? `<strong>${escapeAttr(p.label)}</strong>`
        : `<a href="${escapeAttr(p.href)}">${escapeAttr(p.label)}</a>`,
    )
    .join(" ")

  const dirLinks = opts.directory
    .filter((h) => h.path !== opts.activePath)
    .map(
      (h) =>
        `<a href="${escapeAttr(h.path)}">${escapeAttr(h.label.en ?? h.slug)} (${h.count})</a>`,
    )
    .join(" · ")

  return (
    `<div style="max-width:1200px;margin:0 auto;padding:48px 24px;font-family:Inter,system-ui,sans-serif;color:#1a1c1b">` +
    `<h1 style="font-size:32px;line-height:1.2;margin:0 0 12px">${escapeAttr(opts.heading)}</h1>` +
    `<p style="margin:0 0 24px;max-width:65ch;color:#4a4f4c">${escapeAttr(opts.intro)}</p>` +
    `<ul style="margin:0 0 24px;padding-left:20px;line-height:1.8">${items}</ul>` +
    (pageLinks ? `<nav style="margin:0 0 24px">${pageLinks}</nav>` : "") +
    (dirLinks ? `<nav style="line-height:2;color:#4a4f4c">${dirLinks}</nav>` : "") +
    `</div>`
  )
}

/** Shared head/body rewriter for the two crawlable catalogue surfaces. */
function renderCrawlablePage(opts: {
  shell: string
  title: string
  description: string
  canonical: string
  robots?: string
  prev?: string
  next?: string
  body: string
}): Promise<string> {
  const headExtras =
    `<link rel="canonical" href="${escapeAttr(opts.canonical)}">` +
    `<meta property="og:url" content="${escapeAttr(opts.canonical)}">` +
    `<meta name="twitter:title" content="${escapeAttr(opts.title)}">` +
    `<meta name="twitter:description" content="${escapeAttr(opts.description)}">` +
    (opts.robots ? `<meta name="robots" content="${escapeAttr(opts.robots)}">` : "") +
    (opts.prev ? `<link rel="prev" href="${escapeAttr(opts.prev)}">` : "") +
    (opts.next ? `<link rel="next" href="${escapeAttr(opts.next)}">` : "")

  const rewriter = new HTMLRewriter()
    .on("title", {
      element(el) {
        el.setInnerContent(opts.title)
      },
    })
    .on('meta[name="description"]', {
      element(el) {
        el.setAttribute("content", opts.description)
      },
    })
    .on('meta[property="og:title"]', {
      element(el) {
        el.setAttribute("content", opts.title)
      },
    })
    .on('meta[property="og:description"]', {
      element(el) {
        el.setAttribute("content", opts.description)
      },
    })
    .on("head", {
      element(el) {
        el.append(headExtras, { html: true })
      },
    })

  // Body injection is opt-in: a page we ask Google not to index gets the meta
  // treatment only, since its link list would be work nobody reads.
  if (opts.body) {
    rewriter.on("div#root", {
      element(el) {
        el.setInnerContent(opts.body, { html: true })
      },
    })
  }

  return rewriter.transform(plainShell(opts.shell)).text()
}

function hubHeading(hub: HubItem): string {
  const label = hub.label.en ?? hub.slug
  if (hub.kind === "country") return `Verified charities in ${label}`
  if (hub.kind === "cause") return `Verified charities working on ${label}`
  return `Charities verified through ${label}`
}

function hubIntro(hub: HubItem): string {
  const label = hub.label.en ?? hub.slug
  if (hub.kind === "registry" && hub.description?.en) return hub.description.en
  if (hub.kind === "country") {
    return `${hub.count} organisations registered in ${label}, each linking to the filing its regulator published.`
  }
  return `${hub.count} organisations tagged ${label}. Every one links to a filing you can open yourself — we don't rank them.`
}

/** `/charities/{country|cause|registry}/{slug}` */
async function handleHubPage(
  request: Request,
  env: Env,
  kind: HubItem["kind"],
  slug: string,
): Promise<Response> {
  const url = new URL(request.url)
  const page = Math.max(1, parseInt(url.searchParams.get("page") || "1", 10) || 1)

  // The shell is read before the cache lookup because its build token is part
  // of the cache key — see fetchShell.
  const { html: shell, version } = await fetchShell(request, env)

  const cache = (caches as unknown as { default: Cache }).default
  const cacheKey = new Request(
    `${SITE_BASE}${url.pathname}?v=${version}${page > 1 ? `&page=${page}` : ""}`,
  )
  const cached = await cache.match(cacheKey)
  if (cached) return cached

  const hubs = await fetchHubIndex()
  if (!hubs) return plainShell(shell) // API down → plain SPA, which retries client-side

  const group =
    kind === "country" ? hubs.countries : kind === "cause" ? hubs.causes : hubs.registries
  const hub = group.find((h) => h.slug === slug.toLowerCase())
  // Unknown or below-threshold slug: hand back the untouched shell and let the
  // SPA render "no such section". Never fabricate a page for it.
  if (!hub) return plainShell(shell)

  const listing = await fetchCharityPage(hubApiQuery(hub, page))
  if (!listing) return plainShell(shell)

  const pages = totalPages(listing.count)
  const canonical = `${SITE_BASE}${pageHref(hub.path, page)}`
  const heading = hubHeading(hub)
  const pageSuffix = page > 1 ? ` — page ${page} of ${pages}` : ""
  const title = clamp(`${heading}${pageSuffix} · TrustGive`, 70)
  const description = clamp(hubIntro(hub), 160)

  const body = crawlBody({
    heading,
    intro: hubIntro(hub),
    charities: listing.results.map((c) => ({
      slug: c.slug,
      name: c.name?.en ?? c.slug,
      tagline: c.tagline?.en ?? "",
    })),
    pages: Array.from({ length: pages }, (_, i) => ({
      href: pageHref(hub.path, i + 1),
      label: `Page ${i + 1}`,
      current: i + 1 === page,
    })),
    directory: [...hubs.registries, ...hubs.countries, ...hubs.causes],
    activePath: hub.path,
  })

  const html = await renderCrawlablePage({
    shell,
    title,
    description,
    canonical,
    prev: page > 1 ? `${SITE_BASE}${pageHref(hub.path, page - 1)}` : undefined,
    next: page < pages ? `${SITE_BASE}${pageHref(hub.path, page + 1)}` : undefined,
    body,
  })

  const response = new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": HTML_CACHE_CONTROL,
    },
  })
  await cache.put(cacheKey, response.clone())
  return response
}

/**
 * `/charities` — the catalogue itself, including `?page=N` and `?bucket=`.
 *
 * Faceted URLs (`?q=`, `?region=`, `?cause=`) are served `noindex, follow`: they
 * are near-duplicates of a hub page that says the same thing with a stable URL,
 * and letting a crawler index every filter combination is how a 370-row
 * catalogue turns into thousands of thin URLs. `follow` still lets link value
 * flow through to the charity pages.
 */
async function handleCatalogPage(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url)
  const page = Math.max(1, parseInt(url.searchParams.get("page") || "1", 10) || 1)
  const bucket = (url.searchParams.get("bucket") || "").toLowerCase()
  const validBucket = ["people", "animals", "planet"].includes(bucket) ? bucket : ""

  const indexableParams = new Set(["page", "bucket"])
  const hasFacet = [...url.searchParams.keys()].some((k) => !indexableParams.has(k))

  const { html: shell, version } = await fetchShell(request, env)

  const cache = (caches as unknown as { default: Cache }).default
  const cacheKey = new Request(
    `${SITE_BASE}/charities?v=${version}&${validBucket ? `bucket=${validBucket}&` : ""}page=${page}`,
  )
  // The facet space is unbounded, so faceted URLs skip the edge cache entirely
  // rather than each taking a slot for a page nobody indexes.
  if (!hasFacet) {
    const cached = await cache.match(cacheKey)
    if (cached) return cached
  }

  // A faceted/search URL gets meta only — building a link list for a filter
  // combination we're telling Google not to index would be wasted work.
  if (hasFacet) {
    const html = await renderCrawlablePage({
      shell,
      title: "Charities · TrustGive",
      description:
        "Filtered view of the TrustGive catalogue. Every organisation links to the filing its regulator published.",
      canonical: `${SITE_BASE}/charities`,
      robots: "noindex, follow",
      body: "",
    })
    return new Response(html, {
      status: 200,
      headers: {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "public, max-age=0, s-maxage=600, must-revalidate",
      },
    })
  }

  const query = new URLSearchParams({
    sort: validBucket ? "largest_revenue" : "most_recent_filing",
    page: String(page),
    page_size: String(CATALOG_PAGE_SIZE),
  })
  if (validBucket) query.set("bucket", validBucket)

  const [listing, hubs] = await Promise.all([
    fetchCharityPage(query.toString()),
    fetchHubIndex(),
  ])
  if (!listing) return plainShell(shell)

  const pages = totalPages(listing.count)
  const extra = validBucket ? `bucket=${validBucket}` : ""
  const canonical = `${SITE_BASE}${pageHref("/charities", page, extra)}`
  const heading = validBucket
    ? `${validBucket[0].toUpperCase()}${validBucket.slice(1)} — verified charities`
    : "Verified charities"
  const pageSuffix = page > 1 ? ` — page ${page} of ${pages}` : ""
  const intro = `${listing.count} organisations, each linking to the filing its regulator published. No ratings, no fees, no account.`

  const body = crawlBody({
    heading,
    intro,
    charities: listing.results.map((c) => ({
      slug: c.slug,
      name: c.name?.en ?? c.slug,
      tagline: c.tagline?.en ?? "",
    })),
    pages: Array.from({ length: pages }, (_, i) => ({
      href: pageHref("/charities", i + 1, extra),
      label: `Page ${i + 1}`,
      current: i + 1 === page,
    })),
    directory: hubs ? [...hubs.registries, ...hubs.countries, ...hubs.causes] : [],
  })

  const html = await renderCrawlablePage({
    shell,
    title: clamp(`${heading}${pageSuffix} · TrustGive`, 70),
    description: clamp(intro, 160),
    canonical,
    prev: page > 1 ? `${SITE_BASE}${pageHref("/charities", page - 1, extra)}` : undefined,
    next: page < pages ? `${SITE_BASE}${pageHref("/charities", page + 1, extra)}` : undefined,
    body,
  })

  const response = new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": HTML_CACHE_CONTROL,
    },
  })
  await cache.put(cacheKey, response.clone())
  return response
}

/**
 * `/` — the homepage meta description, with the catalogue's real size in it.
 *
 * index.html is a static file, so any number written into it goes stale the
 * moment the catalogue changes. It claimed "540+ verified charities across 27
 * countries" while the catalogue held 370 across 10 — the counts predated the
 * July audit. That text is what Google prints under the result, so the wrong
 * number was the most-read sentence on the site.
 *
 * The static tag no longer carries counts at all (it has to stay true when this
 * handler can't run); here we put the live figures back in. On any API failure
 * the untouched shell is served, which is correct rather than merely safe: no
 * claim beats a stale one.
 */
async function handleHomePage(request: Request, env: Env): Promise<Response> {
  const cacheKey = new Request(`${SITE_BASE}/?meta=${SITEMAP_VERSION}`)
  const cache = (caches as unknown as { default: Cache }).default
  const cached = await cache.match(cacheKey)
  if (cached) return cached

  const shell = await env.ASSETS.fetch(request)

  // API unreachable → untouched shell, whose static description carries no
  // counts and therefore stays true.
  const stats = await fetchStats()
  if (!stats?.charities || !stats.countries) return shell

  const description =
    `${stats.charities} verified charities across ${stats.countries} countries. ` +
    `Every one links to the regulator's own filing — IRS Form 990, UK Charity ` +
    `Commission, ACNC. No ratings, no fees, no account.`

  const rewriter = new HTMLRewriter()
    .on('meta[name="description"]', {
      element(el) {
        el.setAttribute("content", clamp(description, 160))
      },
    })
    .on('meta[property="og:description"]', {
      element(el) {
        el.setAttribute("content", clamp(description, 160))
      },
    })
    .on("head", {
      element(el) {
        el.append(`<link rel="canonical" href="${escapeAttr(SITE_BASE)}/">`, { html: true })
      },
    })

  const html = await rewriter.transform(shell).text()
  const response = new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": HTML_CACHE_CONTROL,
    },
  })
  await cache.put(cacheKey, response.clone())
  return response
}

/**
 * Structured data for the three editorial pages (STRATEGY §10, Block C).
 *
 *   /data-sources → Dataset      — the markup Google Dataset Search reads. It is
 *                                  a near-empty index compared with web search,
 *                                  and a catalogue of regulator filings is
 *                                  squarely the kind of thing it indexes.
 *   /about        → Organization — with `sameAs` and a named founder. This is
 *                                  the E-E-A-T groundwork STRATEGY calls the
 *                                  project's weakest point: a site about trust
 *                                  that never says who is behind it.
 *   /api          → WebAPI       — makes the documentation page machine-readable
 *                                  as what it is.
 *
 * Two things are deliberately absent from the Dataset block. There is no
 * `license`: no licence has been chosen for the catalogue, and Google treats
 * that field as a claim about reuse rights — inventing one would be asserting
 * terms on the operator's behalf. And `dateModified` is read from /api/stats/
 * rather than written here, for the same reason the homepage counts are.
 */
async function handleStructuredDataPage(
  request: Request,
  env: Env,
  page: "data-sources" | "about" | "api" | "research",
): Promise<Response> {
  const url = new URL(request.url)
  const canonical = `${SITE_BASE}${url.pathname.replace(/\/$/, "")}`
  const cacheKey = new Request(`${canonical}?ld=${SITEMAP_VERSION}`)
  const cache = (caches as unknown as { default: Cache }).default
  const cached = await cache.match(cacheKey)
  if (cached) return cached

  const shell = await env.ASSETS.fetch(request)

  let jsonLd: Record<string, unknown>

  if (page === "data-sources") {
    const [stats, hubs] = await Promise.all([fetchStats(), fetchHubIndex()])
    // No catalogue figures, no Dataset block: a dataset description that can't
    // say how big or how fresh the dataset is has nothing worth indexing.
    if (!stats?.charities) return shell

    jsonLd = {
      "@context": "https://schema.org",
      "@type": "Dataset",
      name: "TrustGive verified charity catalogue",
      description:
        `${stats.charities} charities across ${stats.countries} countries, each linked to ` +
        `the filing its own regulator published — IRS Form 990, the UK Charity ` +
        `Commission register, the Australian Business Register. Organisations whose ` +
        `filing cannot be opened are not published.`,
      url: canonical,
      isAccessibleForFree: true,
      creator: {
        "@type": "Organization",
        name: "TrustGive",
        url: SITE_BASE,
      },
      ...(stats.last_checked ? { dateModified: stats.last_checked } : {}),
      distribution: [
        {
          "@type": "DataDownload",
          encodingFormat: "application/json",
          contentUrl: `${API_BASE}/api/charities/`,
        },
        {
          "@type": "DataDownload",
          encodingFormat: "application/rss+xml",
          contentUrl: `${API_BASE}/api/feed.rss`,
        },
      ],
      // The registers the records come from, named from the live hub index so
      // this list can't quietly disagree with the catalogue.
      ...(hubs?.registries?.length
        ? {
            isBasedOn: hubs.registries.map((registry) => ({
              "@type": "Dataset",
              name: registry.publisher ?? registry.label.en ?? registry.slug,
            })),
          }
        : {}),
      keywords: ["charity", "nonprofit", "regulator filings", "IRS Form 990", "transparency"],
    }
  } else if (page === "about") {
    jsonLd = {
      "@context": "https://schema.org",
      "@type": "Organization",
      name: "TrustGive",
      url: SITE_BASE,
      description:
        "Charity discovery that links every claim to the regulator's own filing. " +
        "No ratings, no fees, no account.",
      email: "hello@trustgive.org",
      founder: { "@type": "Person", name: "Alex Diachenko" },
      sameAs: ["https://github.com/AlexOpasnost/trustgive"],
    }
  } else if (page === "research") {
    jsonLd = {
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      name: "TrustGive research",
      url: canonical,
      description: STRUCTURED_PAGE_META.research.description,
      publisher: { "@type": "Organization", name: "TrustGive", url: SITE_BASE },
      hasPart: Object.entries(RESEARCH_META).map(([slug, meta]) => ({
        "@type": "Report",
        headline: meta.title.replace(" · TrustGive", ""),
        datePublished: meta.published,
        url: `${SITE_BASE}/research/${slug}`,
      })),
    }
  } else {
    jsonLd = {
      "@context": "https://schema.org",
      "@type": "WebAPI",
      name: "TrustGive API",
      description:
        "Anonymous, read-only JSON API over the TrustGive charity catalogue. " +
        "No key and no account; 60 requests per minute per IP.",
      url: canonical,
      documentation: canonical,
      provider: { "@type": "Organization", name: "TrustGive", url: SITE_BASE },
    }
  }

  const meta = STRUCTURED_PAGE_META[page]
  const headExtras =
    `<link rel="canonical" href="${escapeAttr(canonical)}">` +
    `<meta property="og:url" content="${escapeAttr(canonical)}">` +
    `<meta name="twitter:title" content="${escapeAttr(meta.title)}">` +
    `<meta name="twitter:description" content="${escapeAttr(meta.description)}">` +
    `<script type="application/ld+json">${JSON.stringify(jsonLd).replace(/</g, "\\u003c")}</script>`

  const html = await new HTMLRewriter()
    .on("title", {
      element(el) {
        el.setInnerContent(meta.title)
      },
    })
    .on('meta[name="description"]', {
      element(el) {
        el.setAttribute("content", meta.description)
      },
    })
    .on('meta[property="og:title"]', {
      element(el) {
        el.setAttribute("content", meta.title)
      },
    })
    .on('meta[property="og:description"]', {
      element(el) {
        el.setAttribute("content", meta.description)
      },
    })
    .on("head", {
      element(el) {
        el.append(headExtras, { html: true })
      },
    })
    .transform(shell)
    .text()

  const response = new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": HTML_CACHE_CONTROL,
    },
  })
  await cache.put(cacheKey, response.clone())
  return response
}

/** Path → which structured-data block that page gets. Trailing slash stripped
 *  by the caller, so both `/about` and `/about/` resolve. */
const STRUCTURED_DATA_PAGES: Record<string, "data-sources" | "about" | "api" | "research"> = {
  "/data-sources": "data-sources",
  "/about": "about",
  "/api": "api",
  "/research": "research",
}

/**
 * Per-article head copy and dates, mirroring the locale strings and
 * content/research.ts.
 *
 * A research piece that a crawler sees under the homepage's title is a piece
 * nobody will ever cite, and `Report` markup with `datePublished` is what makes
 * it eligible to appear as a dated document rather than a page of a site.
 */
const RESEARCH_META: Record<
  string,
  { title: string; description: string; published: string }
> = {
  "how-old-is-charity-financial-data": {
    title: "Nobody can tell you what a charity spent last year · TrustGive",
    description:
      "Across 365 organisations, not one has financial data covering a period that " +
      "ended within the last twelve months. The median is 31 months, and that is " +
      "the filing system working as designed.",
    published: "2026-08-03",
  },
  "what-we-could-not-verify": {
    title: "A third of the charities we assembled could not be verified · TrustGive",
    description:
      "541 organisations in, 369 with a regulator document that opens. The 172 that " +
      "failed cluster by country, not by charity — and almost none of it is broken links.",
    published: "2026-08-03",
  },
}

/**
 * Head copy for those pages, mirroring the English locale strings.
 *
 * The SPA sets `document.title` after it mounts, so a crawler reading the raw
 * response saw the shell's generic "TrustGive — Verified charity discovery" on
 * all three — the same title as the homepage, which is how a page ends up
 * filed as a duplicate. Kept in English because that is what an unauthenticated
 * crawler gets; the reader still sees their own language once React renders.
 */
const STRUCTURED_PAGE_META: Record<
  "data-sources" | "about" | "api" | "research",
  { title: string; description: string }
> = {
  "data-sources": {
    title: "Data sources · TrustGive",
    description:
      "Everything in the catalogue comes from a public register. Which ones, " +
      "what each covers, and where each falls short.",
  },
  about: {
    title: "About · TrustGive",
    description:
      "Who builds and runs TrustGive, how it is funded, what it deliberately " +
      "cannot do, and how to report an error in the data.",
  },
  api: {
    title: "Public API · TrustGive",
    description:
      "The whole catalogue as JSON. No key, no account, 60 requests per minute. " +
      "Endpoints, filters, examples and the generated OpenAPI schema.",
  },
  research: {
    title: "Research · TrustGive",
    description:
      "Findings from auditing a catalogue of regulator filings: what could not be " +
      "verified, why it clusters by country, and where naive verification lies.",
  },
}

/**
 * `/research/{slug}` — head copy and `Report` markup for one published finding.
 *
 * Only the head is rendered here. The article body stays in the SPA and its
 * locale files rather than being duplicated into the Worker: two copies of a
 * thousand words of prose would drift, and a research piece that says different
 * things in different places is worse than one Google renders a beat late. What
 * decides whether the piece is indexed at all — a distinct title, a real
 * description, a date and an author — is server-rendered.
 */
async function handleResearchArticle(
  request: Request,
  env: Env,
  slug: string,
): Promise<Response> {
  const meta = RESEARCH_META[slug]
  const shell = await env.ASSETS.fetch(request)
  // Unknown slug: hand back the shell and let the SPA say "no such piece".
  if (!meta) return shell

  const canonical = `${SITE_BASE}/research/${slug}`
  const cacheKey = new Request(`${canonical}?ld=${SITEMAP_VERSION}`)
  const cache = (caches as unknown as { default: Cache }).default
  const cached = await cache.match(cacheKey)
  if (cached) return cached

  const headline = meta.title.replace(" · TrustGive", "")
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Report",
    headline,
    description: meta.description,
    datePublished: meta.published,
    url: canonical,
    inLanguage: ["en", "ru"],
    author: { "@type": "Organization", name: "TrustGive", url: SITE_BASE },
    publisher: { "@type": "Organization", name: "TrustGive", url: SITE_BASE },
    isAccessibleForFree: true,
    license: undefined,
  }
  delete (jsonLd as Record<string, unknown>).license

  const headExtras =
    `<link rel="canonical" href="${escapeAttr(canonical)}">` +
    `<meta property="og:url" content="${escapeAttr(canonical)}">` +
    `<meta property="article:published_time" content="${escapeAttr(meta.published)}">` +
    `<meta name="twitter:title" content="${escapeAttr(meta.title)}">` +
    `<meta name="twitter:description" content="${escapeAttr(meta.description)}">` +
    `<script type="application/ld+json">${JSON.stringify(jsonLd).replace(/</g, "\\u003c")}</script>`

  const html = await new HTMLRewriter()
    .on("title", {
      element(el) {
        el.setInnerContent(meta.title)
      },
    })
    .on('meta[name="description"]', {
      element(el) {
        el.setAttribute("content", meta.description)
      },
    })
    .on('meta[property="og:title"]', {
      element(el) {
        el.setAttribute("content", meta.title)
      },
    })
    .on('meta[property="og:description"]', {
      element(el) {
        el.setAttribute("content", meta.description)
      },
    })
    .on('meta[property="og:type"]', {
      element(el) {
        el.setAttribute("content", "article")
      },
    })
    .on("head", {
      element(el) {
        el.append(headExtras, { html: true })
      },
    })
    .transform(shell)
    .text()

  const response = new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": HTML_CACHE_CONTROL,
    },
  })
  await cache.put(cacheKey, response.clone())
  return response
}

const RESEARCH_ARTICLE = /^\/research\/([^/]+)\/?$/

// Order matters: the legit page adds a `/legit` segment, so it's matched before
// the single-segment detail regex below.
const LEGIT_DETAIL = /^\/charities\/([^/]+)\/legit\/?$/
const HUB_PAGE = /^\/charities\/(country|cause|registry)\/([^/]+)\/?$/
const CHARITY_DETAIL = /^\/charities\/([^/]+)\/?$/
const CATALOG_PAGE = /^\/charities\/?$/

/**
 * IndexNow auto-indexing (v3.20).
 *
 * IndexNow lets us instantly notify Bing + Yandex (and any participating engine)
 * about our URLs instead of waiting for a crawl. Ownership is proven by hosting
 * `{key}.txt` at the site root. A daily Cron Trigger (see wrangler.jsonc) calls
 * submitIndexNow(), which reads our own sitemap and submits every URL — so new
 * charities, legit pages, and future SEO pages get picked up without any manual
 * Search-Console work. Yandex coverage is a bonus for the RU side of the catalog.
 */
const INDEXNOW_KEY = "3eba784fdefc58deb12405d6ca68bdf7"

async function submitIndexNow(): Promise<{ submitted: number; status: number }> {
  let urls: string[] = []
  try {
    // Build the sitemap in-process rather than fetching our own public URL —
    // a Worker subrequest to its own hostname doesn't re-enter this handler and
    // came back empty. handleSitemap() hits the (different-host) API directly.
    const xml = await (await handleSitemap()).text()
    urls = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) =>
      m[1].replace(/&amp;/g, "&"),
    )
  } catch {
    // Sitemap build failed — nothing to submit this run.
  }
  if (!urls.length) return { submitted: 0, status: 0 }

  // IndexNow accepts up to 10,000 URLs per request.
  const payload = {
    host: "trustgive.org",
    key: INDEXNOW_KEY,
    keyLocation: `${SITE_BASE}/${INDEXNOW_KEY}.txt`,
    urlList: urls.slice(0, 10000),
  }
  try {
    const resp = await fetch("https://api.indexnow.org/indexnow", {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify(payload),
    })
    return { submitted: payload.urlList.length, status: resp.status }
  } catch {
    return { submitted: 0, status: 0 }
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)

    // IndexNow ownership proof: the engine fetches this file and checks it
    // contains the key. Served verbatim as text.
    if (url.pathname === `/${INDEXNOW_KEY}.txt`) {
      return new Response(INDEXNOW_KEY, {
        headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=86400" },
      })
    }

    // On-demand submit (same work the daily cron does) — handy for a manual
    // re-ping after a big catalogue update. Only ever submits our own sitemap URLs.
    if (url.pathname === "/_indexnow") {
      const r = await submitIndexNow()
      return new Response(JSON.stringify(r), {
        headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
      })
    }

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

    // Homepage: put the catalogue's real size into the meta description.
    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "")) {
      return handleHomePage(request, env)
    }

    // Editorial pages that carry structured data (Dataset / Organization /
    // WebAPI). Client-rendered, so the JSON-LD has to be injected at the edge —
    // Dataset Search and the rich-result parsers don't run our JavaScript.
    if (request.method === "GET") {
      const structured = STRUCTURED_DATA_PAGES[url.pathname.replace(/\/$/, "")]
      if (structured) {
        return handleStructuredDataPage(request, env, structured)
      }
      // Checked after the index so "/research" itself doesn't fall in here.
      const researchMatch = RESEARCH_ARTICLE.exec(url.pathname)
      if (researchMatch) {
        return handleResearchArticle(request, env, decodeURIComponent(researchMatch[1]))
      }
    }

    // "Is X legitimate?" landing (`/charities/{slug}/legit`, GET only) gets its
    // own FAQPage meta. Checked before the detail regex — it has an extra path
    // segment the single-segment detail pattern wouldn't match anyway.
    const legitMatch = request.method === "GET" && LEGIT_DETAIL.exec(url.pathname)
    if (legitMatch) {
      return handleLegitMeta(request, env, decodeURIComponent(legitMatch[1]))
    }

    // Hub sections (v3.21). Matched before CHARITY_DETAIL: both are under
    // /charities/, and a hub carries an extra path segment.
    const hubMatch = request.method === "GET" && HUB_PAGE.exec(url.pathname)
    if (hubMatch) {
      return handleHubPage(
        request,
        env,
        hubMatch[1] as HubItem["kind"],
        decodeURIComponent(hubMatch[2]),
      )
    }

    // The catalogue itself — rendered with its charity links and page links so
    // a crawler doesn't have to run our JavaScript to find 370 charities.
    if (request.method === "GET" && CATALOG_PAGE.test(url.pathname)) {
      return handleCatalogPage(request, env)
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

  // Daily Cron Trigger (wrangler.jsonc → triggers.crons): re-submit every
  // sitemap URL to IndexNow so Bing/Yandex pick up new + changed pages
  // automatically, with zero manual Search-Console work.
  async scheduled(_event: ScheduledController, _env: Env, ctx: ExecutionContext): Promise<void> {
    ctx.waitUntil(submitIndexNow())
  },
} satisfies ExportedHandler<Env>
