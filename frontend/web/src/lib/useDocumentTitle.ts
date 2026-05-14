/**
 * useDocumentTitle — sets document.title for the current route.
 *
 * No react-helmet dependency: this is a SPA with ~4 routes, and the only
 * head tag that needs to change per route is <title>. A 12-line effect is
 * the right size for the problem.
 *
 * Pass the page-specific part only; the hook appends the " · TrustGive"
 * suffix. Pass null while data is still loading to leave the title untouched
 * (avoids a "null · TrustGive" flash on detail pages).
 *
 * On unmount the title is restored to the bare brand name so a route with
 * no explicit title doesn't inherit the previous page's.
 */

import { useEffect } from "react"

const SUFFIX = "TrustGive"
const DEFAULT_TITLE = "TrustGive — Verified charity discovery"

export function useDocumentTitle(title: string | null): void {
  useEffect(() => {
    if (title === null) return
    document.title = title ? `${title} · ${SUFFIX}` : DEFAULT_TITLE
    return () => {
      document.title = DEFAULT_TITLE
    }
  }, [title])
}
