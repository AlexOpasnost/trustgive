/**
 * TanStack Query hooks — colocated for reuse across pages.
 *
 * staleTime tuning rule: align with backend Cache-Control.
 *   - /api/charities/featured/ → s-maxage=3600 → staleTime: 1h
 */

import { useQuery } from "@tanstack/react-query"

import { api } from "@/lib/api"
import type { Bucket } from "@/types/api"

/**
 * Catalogue counts (v3.22). Backend ships `s-maxage=3600`.
 *
 * Callers must render nothing rather than a placeholder while this is loading:
 * a wrong number on a page about verifiable claims is worse than no number, and
 * a wrong one is exactly what this endpoint replaced.
 */
export function useStats() {
  return useQuery({
    queryKey: ["stats"],
    queryFn: ({ signal }) => api.getStats({ signal }),
    staleTime: 60 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
    retry: 1,
  })
}

/**
 * Hub index (v3.21). Backend ships `s-maxage=3600`; the payload only changes
 * when a grouping crosses the publication threshold, so an hour of client
 * staleness is generous.
 */
export function useHubs() {
  return useQuery({
    queryKey: ["hubs"],
    queryFn: ({ signal }) => api.listHubs({ signal }),
    staleTime: 60 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
    retry: 1,
  })
}

/**
 * Featured charities, optionally filtered by bucket (DESIGN.md v3.0 §A).
 *
 * Backend endpoint (`GET /api/charities/featured/?bucket=people|animals|planet`)
 * ships with `Cache-Control: public, s-maxage=3600` — 1 hour. We mirror that on
 * the client to avoid refetching while the CDN edge would still hand us the
 * same payload.
 */
export function useFeaturedCharities(args: { bucket?: Bucket } = {}) {
  const { bucket } = args
  return useQuery({
    queryKey: ["charities", "featured", bucket ?? "all"],
    queryFn: ({ signal }) => api.featuredCharities({ bucket }, { signal }),
    staleTime: 60 * 60 * 1000, // 1h — matches backend s-maxage
    gcTime: 60 * 60 * 1000,
    retry: 1,
  })
}
