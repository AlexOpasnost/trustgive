/**
 * Pagination — numbered page links (v3.21).
 *
 * Why this exists alongside "Load more": a button is invisible to a crawler.
 * Until v3.21 the catalogue rendered 60 cards and hid the other 310 behind
 * `fetchNextPage()`, so 310 charity pages had no internal link pointing at them
 * and Google filed them as "Discovered — currently not indexed". These are real
 * `<a href>` elements (react-router `Link` renders one), which is the whole
 * point — a crawler must be able to reach page 7 without running our JavaScript.
 *
 * "Load more" stays for humans: it's the better interaction, and the two are
 * consistent because both read the same `?page=` parameter.
 */

import { ArrowLeft02Icon, ArrowRight01Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

type Props = {
  currentPage: number
  totalPages: number
  /** Build the href for a given page number, preserving the page's own filters. */
  buildHref: (page: number) => string
}

/**
 * Page numbers to render: always the first, the last, and a window of two
 * either side of the current page. Gaps become an ellipsis. Below 10 pages
 * everything is listed — the catalogue is currently 7 pages, so in practice a
 * crawler sees every page number on every page.
 */
function pageWindow(current: number, total: number): (number | "gap")[] {
  if (total <= 10) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  const keep = new Set<number>([1, total])
  for (let p = current - 2; p <= current + 2; p += 1) {
    if (p >= 1 && p <= total) keep.add(p)
  }
  const sorted = [...keep].sort((a, b) => a - b)
  const out: (number | "gap")[] = []
  let previous = 0
  for (const p of sorted) {
    if (previous && p - previous > 1) out.push("gap")
    out.push(p)
    previous = p
  }
  return out
}

export function Pagination({ currentPage, totalPages, buildHref }: Props) {
  const { t } = useTranslation()

  if (totalPages <= 1) return null

  const pages = pageWindow(currentPage, totalPages)
  const linkBase =
    "inline-flex items-center justify-center min-w-9 h-9 px-3 rounded-md text-body-sm border transition-colors"

  return (
    <nav
      className="mt-10 flex flex-wrap items-center justify-center gap-2"
      aria-label={t("catalog.pagination.label")}
    >
      {currentPage > 1 && (
        <Link
          to={buildHref(currentPage - 1)}
          rel="prev"
          className={`${linkBase} border-rule text-ink-2 hover:text-ink hover:border-ink gap-1.5`}
        >
          <HugeiconsIcon icon={ArrowLeft02Icon} size={14} aria-hidden="true" />
          {t("catalog.pagination.previous")}
        </Link>
      )}

      {pages.map((p, i) =>
        p === "gap" ? (
          <span
            key={`gap-${i}`}
            className="px-1 text-body-sm text-ink-3"
            aria-hidden="true"
          >
            …
          </span>
        ) : p === currentPage ? (
          <span
            key={p}
            aria-current="page"
            className={`${linkBase} border-ink bg-ink text-white font-mono`}
          >
            {p}
          </span>
        ) : (
          <Link
            key={p}
            to={buildHref(p)}
            aria-label={t("catalog.pagination.goToPage", { page: p })}
            className={`${linkBase} border-rule text-ink-2 font-mono hover:text-ink hover:border-ink`}
          >
            {p}
          </Link>
        ),
      )}

      {currentPage < totalPages && (
        <Link
          to={buildHref(currentPage + 1)}
          rel="next"
          className={`${linkBase} border-rule text-ink-2 hover:text-ink hover:border-ink gap-1.5`}
        >
          {t("catalog.pagination.next")}
          <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
        </Link>
      )}
    </nav>
  )
}
