/**
 * CatalogPage — DESIGN_v4.md §6.2 (editorial archive).
 *
 * v4 layout replaces v3.1's grid of cards with a long scrollable archive
 * separated by hairline rules. Photos sit inline beside text; no card
 * chrome, no shadows, no rounded rectangles. Filters are text links in
 * a single sentence, not chip arrays — active filter is underlined.
 *
 * Mobile: each entry stacks photo-above-text per the v4 mobile decision.
 * The CharityArchiveItem component owns its own breakpoint behaviour.
 */

import { useInfiniteQuery } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"

import { CharityArchiveItem } from "@/components/charity/CharityArchiveItem"
import { api, type CharityListParams } from "@/lib/api"
import { BUCKET_SUBFILTERS, REGION_FILTERS } from "@/lib/buckets"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
import { usePreferences } from "@/store/preferences"
import type { Bucket } from "@/types/api"

const PAGE_SIZE = 60
const VALID_BUCKETS: Bucket[] = ["people", "animals", "planet"]

function isBucket(value: string | null): value is Bucket {
  return value !== null && (VALID_BUCKETS as string[]).includes(value)
}

/**
 * Inline text-link filter button. The v4 catalog uses these in place of
 * chips: a row of words separated by middots, with the active one
 * underlined. Hover applies the same underline so the affordance is clear.
 */
function FilterLink({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="font-sans transition-colors duration-150 hover:underline decoration-1 underline-offset-4"
      style={{
        fontSize: "var(--text-ui-md)",
        lineHeight: "var(--text-ui-md--line-height)",
        color: active ? "var(--color-ink-v4)" : "var(--color-ink-3-v4)",
        fontWeight: active ? 600 : 500,
        textDecoration: active ? "underline" : "none",
        textDecorationThickness: "1px",
        textUnderlineOffset: "4px",
      }}
    >
      {children}
    </button>
  )
}

export function CatalogPage() {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const [searchParams, setSearchParams] = useSearchParams()

  const bucketParam = searchParams.get("bucket")
  const bucket: Bucket | undefined = isBucket(bucketParam) ? bucketParam : undefined
  const activeCause = searchParams.get("cause")
  const activeRegion = searchParams.get("region")
  const region = REGION_FILTERS.find((r) => r.slug === activeRegion)
  const countryParam = region?.countries?.length ? region.countries.join(",") : undefined

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
    getNextPageParam: (lastPage) => (lastPage.next ? lastPage.page + 1 : undefined),
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

  const bucketLabel = bucket
    ? t(`homepage.bucket.${bucket}.label`)
    : null
  const headline = bucketLabel
    ? t("catalog.v4.bucketHeadline", { bucket: bucketLabel })
    : t("catalog.v4.totalHeadline", { total: totalCount || "" })

  useDocumentTitle(bucketLabel ?? t("catalog.title"))

  const subfilters = bucket ? BUCKET_SUBFILTERS[bucket] : null

  return (
    <main
      style={{
        background: "var(--color-paper-v4)",
        color: "var(--color-ink-v4)",
      }}
    >
      {/* ============= HEADER ============= */}
      <section className="px-6 lg:px-12 pt-16 lg:pt-24 pb-10 lg:pb-14 max-w-[1280px] mx-auto">
        <p
          className="font-sans uppercase mb-8"
          style={{
            fontSize: "var(--text-ui-sm)",
            lineHeight: "var(--text-ui-sm--line-height)",
            letterSpacing: "0.16em",
            color: "var(--color-ink-3-v4)",
            fontWeight: 500,
          }}
        >
          {t("catalog.v4.eyebrow")}
        </p>
        <h1
          className="font-serif"
          style={{
            fontSize: "clamp(40px, 6vw, 64px)",
            lineHeight: 1.05,
            fontWeight: 400,
            letterSpacing: "-0.015em",
            color: "var(--color-ink-v4)",
          }}
        >
          {headline}
        </h1>
      </section>

      {/* ============= FILTER ROW ============= */}
      <section className="px-6 lg:px-12 pb-8 max-w-[1280px] mx-auto">
        <div
          className="flex flex-wrap items-baseline gap-x-2 gap-y-3 mb-4"
          role="group"
          aria-label={t("catalog.v4.filterLabel")}
        >
          <span
            className="font-sans uppercase mr-2"
            style={{
              fontSize: "var(--text-ui-sm)",
              lineHeight: "var(--text-ui-md--line-height)",
              letterSpacing: "0.14em",
              color: "var(--color-ink-3-v4)",
              fontWeight: 500,
            }}
          >
            {t("catalog.v4.filterLabel")}
          </span>
          <FilterLink active={!bucket} onClick={() => setFilter("bucket", null)}>
            {t("catalog.v4.allBuckets")}
          </FilterLink>
          {VALID_BUCKETS.map((b) => (
            <span key={b} className="flex items-baseline gap-x-2">
              <span style={{ color: "var(--color-rule-soft-v4)" }}>·</span>
              <FilterLink active={bucket === b} onClick={() => setFilter("bucket", b)}>
                {t(`homepage.bucket.${b}.label`)}
              </FilterLink>
            </span>
          ))}
        </div>

        <div
          className="flex flex-wrap items-baseline gap-x-2 gap-y-3 mb-4"
          role="group"
          aria-label={t("catalog.v4.regionLabel")}
        >
          <span
            className="font-sans uppercase mr-2"
            style={{
              fontSize: "var(--text-ui-sm)",
              lineHeight: "var(--text-ui-md--line-height)",
              letterSpacing: "0.14em",
              color: "var(--color-ink-3-v4)",
              fontWeight: 500,
            }}
          >
            {t("catalog.v4.regionLabel")}
          </span>
          {REGION_FILTERS.map((r, i) => {
            const active = (activeRegion ?? null) === r.slug
            return (
              <span key={r.slug ?? "all"} className="flex items-baseline gap-x-2">
                {i > 0 && (
                  <span style={{ color: "var(--color-rule-soft-v4)" }}>·</span>
                )}
                <FilterLink active={active} onClick={() => setFilter("region", r.slug)}>
                  {lang === "ru" ? r.labelRu : r.labelEn}
                </FilterLink>
              </span>
            )
          })}
        </div>

        {subfilters && (
          <div
            className="flex flex-wrap items-baseline gap-x-2 gap-y-3"
            role="group"
            aria-label={t("catalog.v4.causeLabel")}
          >
            <span
              className="font-sans uppercase mr-2"
              style={{
                fontSize: "var(--text-ui-sm)",
                lineHeight: "var(--text-ui-md--line-height)",
                letterSpacing: "0.14em",
                color: "var(--color-ink-3-v4)",
                fontWeight: 500,
              }}
            >
              {t("catalog.v4.causeLabel")}
            </span>
            {subfilters.map((f, i) => {
              const active = (activeCause ?? null) === f.slug
              return (
                <span key={f.slug ?? "all"} className="flex items-baseline gap-x-2">
                  {i > 0 && (
                    <span style={{ color: "var(--color-rule-soft-v4)" }}>·</span>
                  )}
                  <FilterLink active={active} onClick={() => setFilter("cause", f.slug)}>
                    {lang === "ru" ? f.labelRu : f.labelEn}
                  </FilterLink>
                </span>
              )
            })}
          </div>
        )}

        {data && loadedCount > 0 && (
          <p
            className="font-sans mt-6"
            style={{
              fontSize: "var(--text-ui-sm)",
              lineHeight: "var(--text-ui-sm--line-height)",
              color: "var(--color-ink-3-v4)",
            }}
          >
            {t("catalog.v4.loadedOf", { loaded: loadedCount, total: totalCount })}
          </p>
        )}
      </section>

      {/* ============= ARCHIVE ============= */}
      <section className="px-6 lg:px-12 max-w-[1280px] mx-auto pb-24">
        {/* Initial-load skeleton */}
        {isLoading && (
          <div
            aria-hidden="true"
            style={{ borderTop: "1px solid var(--color-rule-v4)" }}
          >
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                style={{ borderBottom: "1px solid var(--color-rule-v4)" }}
                className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-10 py-8 lg:py-10"
              >
                <div className="lg:col-span-5">
                  <div className="aspect-[4/3] skeleton" />
                </div>
                <div className="lg:col-span-7 flex flex-col justify-center gap-3">
                  <div className="skeleton h-3 w-28" />
                  <div className="skeleton h-7 w-2/3" />
                  <div className="skeleton h-4 w-3/4" />
                  <div className="skeleton h-3 w-1/2" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error state */}
        {isError && (
          <div className="py-16 text-center">
            <p
              className="font-serif italic"
              style={{
                fontSize: "var(--text-body-lg)",
                lineHeight: "var(--text-body-lg--line-height)",
                color: "var(--color-ink-2-v4)",
              }}
            >
              {t("common.errorBody")}
            </p>
          </div>
        )}

        {/* Empty state */}
        {data && loadedCount === 0 && (
          <div className="py-16 text-center">
            <p
              className="font-serif italic"
              style={{
                fontSize: "var(--text-body-lg)",
                lineHeight: "var(--text-body-lg--line-height)",
                color: "var(--color-ink-2-v4)",
              }}
            >
              {t("catalog.tryRemoving")}
            </p>
          </div>
        )}

        {/* Archive entries */}
        {data && loadedCount > 0 && (
          <div style={{ borderTop: "1px solid var(--color-rule-v4)" }}>
            {allResults.map((charity) => (
              <div
                key={charity.slug}
                style={{ borderBottom: "1px solid var(--color-rule-v4)" }}
              >
                <CharityArchiveItem charity={charity} />
              </div>
            ))}

            {hasNextPage && (
              <div className="mt-10 lg:mt-14 flex justify-center">
                <button
                  type="button"
                  onClick={() => fetchNextPage()}
                  disabled={isFetchingNextPage}
                  className="font-sans group inline-flex items-baseline gap-2 disabled:opacity-60"
                  style={{
                    fontSize: "var(--text-ui-md)",
                    lineHeight: "var(--text-ui-md--line-height)",
                    color: "var(--color-link)",
                    fontWeight: 500,
                  }}
                >
                  <span className="underline decoration-1 underline-offset-4 group-hover:no-underline">
                    {isFetchingNextPage
                      ? t("catalog.v4.loading")
                      : t("catalog.v4.showMore", { n: PAGE_SIZE })}
                  </span>
                  <span aria-hidden="true">→</span>
                </button>
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  )
}
