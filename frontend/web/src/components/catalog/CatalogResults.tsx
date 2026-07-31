/**
 * CatalogResults — the charity grid shared by the catalogue and every hub page
 * (v3.21).
 *
 * Both surfaces show the same thing: a filtered slice of the catalogue, 60 cards
 * at a time, with "Load more" for people and numbered page links for crawlers.
 * Keeping one component means a hub page can never drift from the catalogue in
 * how it paginates, counts, or reports an empty result.
 *
 * The query starts at `page` rather than always at 1, so `?page=4` renders
 * charities 181–240 directly instead of forcing four round-trips — which is what
 * a crawler landing on a deep page needs, and what a human sharing a link
 * expects.
 */

import { useInfiniteQuery } from "@tanstack/react-query"
import { useEffect, useRef } from "react"
import { useTranslation } from "react-i18next"

import { CharityCard } from "@/components/charity/CharityCard"
import { Pagination } from "@/components/catalog/Pagination"
import { Button } from "@/components/ui/Button"
import { api, type CharityListParams } from "@/lib/api"

export const CATALOG_PAGE_SIZE = 60

type Props = {
  /** Filters for this surface. Must be referentially stable per render input. */
  params: Omit<CharityListParams, "page" | "page_size">
  /** 1-based page to start from (from `?page=`). */
  page: number
  /** Build the href for page N, preserving this surface's own filters. */
  buildPageHref: (page: number) => string
  /** Copy shown when the filters match nothing. */
  empty: { title: string; body: string }
}

export function CatalogResults({ params, page, buildPageHref, empty }: Props) {
  const { t } = useTranslation()

  const {
    data,
    isLoading,
    isError,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ["charities", params, page],
    initialPageParam: page,
    queryFn: ({ pageParam, signal }) =>
      api.listCharities(
        { ...params, page: pageParam as number, page_size: CATALOG_PAGE_SIZE },
        { signal },
      ),
    getNextPageParam: (lastPage) => (lastPage.next ? lastPage.page + 1 : undefined),
  })

  const pages = data?.pages ?? []
  const allResults = pages.flatMap((p) => p.results)
  const totalCount = pages[0]?.count ?? 0
  const loadedCount = allResults.length
  const totalPages = Math.max(1, Math.ceil(totalCount / CATALOG_PAGE_SIZE))
  const firstIndex = (page - 1) * CATALOG_PAGE_SIZE + 1

  // Following a page link from the pagination bar leaves the viewport at the
  // bottom of the previous page, where the new page's last rows happen to be.
  // Skip the initial mount so a deep link doesn't fight the browser's own
  // scroll restoration.
  const mounted = useRef(false)
  useEffect(() => {
    if (!mounted.current) {
      mounted.current = true
      return
    }
    window.scrollTo({ top: 0, behavior: "auto" })
  }, [page])

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className="bg-surface-raised border border-rule rounded-md overflow-hidden"
          >
            <div className="aspect-[3/2] skeleton" />
            <div className="p-5">
              <div className="skeleton h-5 w-2/3 mb-2" />
              <div className="skeleton h-4 w-1/2 mb-3" />
              <div className="skeleton h-3 w-3/4" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <div className="border border-rule rounded-md p-12 text-center">
        <h2 className="text-h3 font-semibold text-ink mb-2">{t("common.error")}</h2>
        <p className="text-body text-ink-2">{t("common.errorBody")}</p>
      </div>
    )
  }

  if (loadedCount === 0) {
    return (
      <div className="border border-rule rounded-md p-12 text-center">
        <h2 className="text-h3 font-semibold text-ink mb-2">{empty.title}</h2>
        <p className="text-body text-ink-2 max-w-[60ch] mx-auto">{empty.body}</p>
      </div>
    )
  }

  return (
    <>
      <p className="text-body-sm text-ink-3 mb-6">
        {t("catalog.showing", {
          from: firstIndex,
          to: firstIndex + loadedCount - 1,
          count: totalCount,
        })}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {allResults.map((charity) => (
          <CharityCard key={charity.slug} charity={charity} />
        ))}
      </div>

      {hasNextPage && (
        <div className="mt-12 flex justify-center">
          <Button
            variant="secondary"
            size="lg"
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
          >
            {isFetchingNextPage ? t("catalog.loadingMore") : t("catalog.loadMore")}
          </Button>
        </div>
      )}

      <Pagination
        currentPage={page}
        totalPages={totalPages}
        buildHref={buildPageHref}
      />
    </>
  )
}
