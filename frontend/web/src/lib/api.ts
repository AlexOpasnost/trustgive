/**
 * API client — wraps fetch with the API base URL.
 *
 * NOTE: For Phase 4 we use a hand-written client. Once Phase 3 backend is running
 * and `/api/schema/` is reachable, regenerate types with:
 *   npm run gen-api
 * Then refactor to use `openapi-fetch`'s typed client against `paths` from
 * `src/api/schema.d.ts`.
 *
 * v3.0 changes:
 *   - `bucket` filter added to listCharities + featuredCharities
 *   - compareCharities endpoint REMOVED (backend returns 404)
 */

import type {
  Bucket,
  Cause,
  Charity,
  CharitySummary,
  PaginatedCharitySummary,
  SourceDocument,
} from "@/types/api"

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? ""

type FetchOptions = {
  signal?: AbortSignal
  headers?: Record<string, string>
}

async function apiFetch<T>(path: string, opts: FetchOptions = {}): Promise<T> {
  const url = `${BASE_URL}${path}`
  const res = await fetch(url, {
    headers: {
      "Accept": "application/json",
      ...(opts.headers ?? {}),
    },
    signal: opts.signal,
  })
  if (!res.ok) {
    let message = `Request failed: ${res.status}`
    try {
      const body = (await res.json()) as { error?: { message?: string } }
      if (body?.error?.message) message = body.error.message
    } catch {
      // ignore — message stays generic
    }
    throw new Error(message)
  }
  return (await res.json()) as T
}

export type CharityListParams = {
  cause?: string[]
  /**
   * ISO 3166-1 alpha-2 code(s). Single code for one country
   * (`country: "GB"`) or comma-separated for regional groups
   * (`country: "GB,DE,NL,CH,SE,FR"` for Europe). v3.7+ backend
   * BaseInFilter accepts both forms.
   */
  country?: string
  size?: "small" | "medium" | "large"
  verification_status?: "verified" | "listed" | "stale"
  badges?: string[]
  bucket?: Bucket
  q?: string
  lang?: "en" | "ru"
  sort?: "most_recent_filing" | "largest_revenue" | "highest_program_pct" | "alphabetical"
  page?: number
  page_size?: number
}

export type FeaturedParams = {
  bucket?: Bucket
}

function toQuery(params: Record<string, unknown>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value == null) continue
    if (Array.isArray(value)) {
      if (key === "badges") {
        if (value.length > 0) search.set("badges", value.join(","))
      } else {
        for (const v of value) search.append(key, String(v))
      }
    } else {
      search.set(key, String(value))
    }
  }
  const qs = search.toString()
  return qs ? `?${qs}` : ""
}

export const api = {
  listCharities(params: CharityListParams = {}, opts?: FetchOptions) {
    return apiFetch<PaginatedCharitySummary>(`/api/charities/${toQuery(params)}`, opts)
  },
  /**
   * Featured charities for homepage bucket cards (DESIGN.md v3.0 §A).
   * Backend returns a flat array (no pagination wrapper) of ≤6 CharitySummary items.
   * If `bucket` is provided, results are filtered to that bucket.
   * Cache aligned with backend `s-maxage=3600`: TanStack staleTime = 1h.
   */
  featuredCharities(params: FeaturedParams = {}, opts?: FetchOptions) {
    return apiFetch<CharitySummary[]>(`/api/charities/featured/${toQuery(params)}`, opts)
  },
  getCharity(slug: string, opts?: FetchOptions) {
    return apiFetch<Charity>(`/api/charities/${slug}/`, opts)
  },
  listSourceDocuments(slug: string, opts?: FetchOptions) {
    return apiFetch<SourceDocument[]>(`/api/charities/${slug}/source-documents/`, opts)
  },
  listCauses(opts?: FetchOptions) {
    return apiFetch<Cause[]>(`/api/causes/`, opts)
  },
  logDonationRedirect(payload: {
    charity_slug: string
    lang: "en" | "ru"
    source_page?: "detail" | "comparison" | "seo_landing" | "search"
    client_event_id: string
  }) {
    return fetch(`${BASE_URL}/api/events/donation-redirect/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      keepalive: true,
    }).catch(() => {
      // best-effort; never block UI
    })
  },
}
