/**
 * CatalogPage — DESIGN.md v3.1 §I (sub-filter chips) + §J (sidebar removed).
 *
 * v3.1 changes from v3.0:
 *   - Removed entire <aside> sidebar (Country / Size / Verification radios)
 *   - Country becomes a top-bar Chip group
 *   - Cause becomes a top-bar Chip group, populated from BUCKET_SUBFILTERS
 *     when `?bucket=` is active
 *   - Grid is now full-width (no 260px sidebar reservation)
 *   - Implicit defaults: revenue-DESC sort for bucket views, all charities
 *     in the catalog are `verified` by curation so the verification filter
 *     was meaningless to expose
 */

import { useInfiniteQuery } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"

import { CharityCard } from "@/components/charity/CharityCard"
import { Button } from "@/components/ui/Button"
import { Chip } from "@/components/ui/Chip"
import { api, type CharityListParams } from "@/lib/api"
import { BUCKET_SUBFILTERS, REGION_FILTERS } from "@/lib/buckets"
import { usePreferences } from "@/store/preferences"
import type { Bucket } from "@/types/api"

const PAGE_SIZE = 60

const VALID_BUCKETS: Bucket[] = ["people", "animals", "planet"]

function isBucket(value: string | null): value is Bucket {
  return value !== null && (VALID_BUCKETS as string[]).includes(value)
}

export function CatalogPage() {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const [searchParams, setSearchParams] = useSearchParams()

  const bucketParam = searchParams.get("bucket")
  const bucket: Bucket | undefined = isBucket(bucketParam) ? bucketParam : undefined
  const activeCause = searchParams.get("cause")
  // v3.7: replaced single-country filter with regional groups
  // (?region=europe → country=GB,DE,NL,CH,SE,FR). Frontend-only param;
  // translated to comma-separated ISO codes for the backend BaseInFilter.
  const activeRegion = searchParams.get("region")
  const region = REGION_FILTERS.find((r) => r.slug === activeRegion)
  const countryParam = region?.countries?.length ? region.countries.join(",") : undefined

  // v3.15: useInfiniteQuery + Load-more replaces the v3.7 single-page page_size=300
  // approach. Required because the catalog crossed 300 charities (now 541) — the
  // old approach silently truncated 241 charities.
  const baseParams: Omit<CharityListParams, "page" | "page_size"> = {
    cause: activeCause ? [activeCause] : [],
    country: countryParam,
    bucket,
    sort: bucket ? "largest_revenue" : "most_recent_filing",
  }

  const {
    data,
    isLoading,
    isError,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ["charities", baseParams],
    initialPageParam: 1,
    queryFn: ({ pageParam, signal }) =>
      api.listCharities(
        { ...baseParams, page: pageParam as number, page_size: PAGE_SIZE },
        { signal },
      ),
    getNextPageParam: (lastPage) =>
      lastPage.next ? lastPage.page + 1 : undefined,
  })

  const pages = data?.pages ?? []
  const allResults = pages.flatMap((p) => p.results)
  const totalCount = pages[0]?.count ?? 0
  const loadedCount = allResults.length

  const setFilter = (key: string, value: string | null) => {
    const next = new URLSearchParams(searchParams)
    if (value == null || value === "") next.delete(key)
    else next.set(key, value)
    next.delete("page")
    setSearchParams(next, { replace: true })
  }

  const headerTitle = bucket ? t(`bucket.${bucket}.pageTitle`) : t("catalog.title")
  const headerSubtitle = bucket ? t(`bucket.${bucket}.pageSubtitle`) : null

  const subfilters = bucket ? BUCKET_SUBFILTERS[bucket] : null

  return (
    <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12">
      <header className="mb-8">
        <h1 className="font-serif text-h1 font-semibold text-ink leading-tight">
          {headerTitle}
        </h1>
        {headerSubtitle && (
          <p className="text-body text-ink-2 mt-3 max-w-2xl">{headerSubtitle}</p>
        )}
        {data && loadedCount > 0 && (
          <p className="text-body-sm text-ink-3 mt-4">
            {t("catalog.showing", {
              from: 1,
              to: loadedCount,
              count: totalCount,
            })}
          </p>
        )}
      </header>

      {/* === Region chips (v3.7 — replaces single-country filter) === */}
      <div className="flex flex-wrap gap-2 mb-3" role="group" aria-label={t("catalog.country")}>
        {REGION_FILTERS.map((r) => {
          const active = (activeRegion ?? null) === r.slug
          return (
            <Chip
              key={r.slug ?? "all"}
              active={active}
              onClick={() => setFilter("region", r.slug)}
            >
              {lang === "ru" ? r.labelRu : r.labelEn}
            </Chip>
          )
        })}
      </div>

      {/* === Sub-cause chips (only when bucket is active) === */}
      {subfilters && (
        <div
          className="flex flex-wrap gap-2 mb-8"
          role="group"
          aria-label={t("catalog.cause")}
        >
          {subfilters.map((f) => {
            const active = (activeCause ?? null) === f.slug
            return (
              <Chip
                key={f.slug ?? "all"}
                active={active}
                onClick={() => setFilter("cause", f.slug)}
              >
                {lang === "ru" ? f.labelRu : f.labelEn}
              </Chip>
            )
          })}
        </div>
      )}

      {!subfilters && <div className="mb-8" />}

      {/* === Grid === */}
      <main>
        {isLoading && (
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
        )}

        {isError && (
          <div className="border border-rule rounded-md p-12 text-center">
            <h2 className="text-h3 font-semibold text-ink mb-2">{t("common.error")}</h2>
            <p className="text-body text-ink-2">{t("common.errorBody")}</p>
          </div>
        )}

        {data && loadedCount === 0 && (
          <div className="border border-rule rounded-md p-12 text-center">
            <h2 className="text-h3 font-semibold text-ink mb-2">
              {t("catalog.noResults")}
            </h2>
            <p className="text-body text-ink-2">{t("catalog.tryRemoving")}</p>
          </div>
        )}

        {data && loadedCount > 0 && (
          <>
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
                  {isFetchingNextPage
                    ? t("catalog.loadingMore")
                    : t("catalog.loadMore")}
                </Button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
