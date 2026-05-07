/**
 * TanStack Query hooks — colocated for reuse across pages.
 *
 * staleTime tuning rule: align with backend Cache-Control.
 *   - /api/charities/featured/ → s-maxage=3600 → staleTime: 1h
 */

import { useQuery } from "@tanstack/react-query"

import { api } from "@/lib/api"

/**
 * Featured charities for the homepage strip.
 *
 * Backend endpoint (`GET /api/charities/featured/`) ships with `Cache-Control:
 * public, s-maxage=3600` — 1 hour. We mirror that on the client to avoid
 * refetching while the CDN edge would still hand us the same payload.
 */
export function useFeaturedCharities() {
  return useQuery({
    queryKey: ["charities", "featured"],
    queryFn: ({ signal }) => api.featuredCharities({ signal }),
    staleTime: 60 * 60 * 1000, // 1h — matches backend s-maxage
    gcTime: 60 * 60 * 1000,
    retry: 1,
  })
}
