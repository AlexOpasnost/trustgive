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
    { loc: `${base}/data-sources`, priority: "0.7" },
    { loc: `${base}/about`, priority: "0.6" },
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
  const cache = (caches as unknown as { default: Cache }).default
  const cacheKey = new Request(canonical)
  const cached = await cache.match(cacheKey)
  if (cached) return cached

  const shell = await env.ASSETS.fetch(request)

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

  if (!payload || !payload.h1) return shell // 404 or API down → plain SPA

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

  const transformed = rewriter.transform(shell)
  const html = await transformed.text()
  const response = new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "public, max-age=0, s-maxage=3600, must-revalidate",
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
  shell: Response
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

  return rewriter.transform(opts.shell).text()
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

  const cache = (caches as unknown as { default: Cache }).default
  const cacheKey = new Request(`${SITE_BASE}${url.pathname}${page > 1 ? `?page=${page}` : ""}`)
  const cached = await cache.match(cacheKey)
  if (cached) return cached

  const shell = await env.ASSETS.fetch(request)

  const hubs = await fetchHubIndex()
  if (!hubs) return shell // API down → plain SPA, which retries client-side

  const group =
    kind === "country" ? hubs.countries : kind === "cause" ? hubs.causes : hubs.registries
  const hub = group.find((h) => h.slug === slug.toLowerCase())
  // Unknown or below-threshold slug: hand back the untouched shell and let the
  // SPA render "no such section". Never fabricate a page for it.
  if (!hub) return shell

  const listing = await fetchCharityPage(hubApiQuery(hub, page))
  if (!listing) return shell

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
      "Cache-Control": "public, max-age=0, s-maxage=3600, must-revalidate",
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

  const cache = (caches as unknown as { default: Cache }).default
  const cacheKey = new Request(
    `${SITE_BASE}/charities?${validBucket ? `bucket=${validBucket}&` : ""}page=${page}`,
  )
  // The facet space is unbounded, so faceted URLs skip the edge cache entirely
  // rather than each taking a slot for a page nobody indexes.
  if (!hasFacet) {
    const cached = await cache.match(cacheKey)
    if (cached) return cached
  }

  const shell = await env.ASSETS.fetch(request)

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
  if (!listing) return shell

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
      "Cache-Control": "public, max-age=0, s-maxage=3600, must-revalidate",
    },
  })
  await cache.put(cacheKey, response.clone())
  return response
}

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
