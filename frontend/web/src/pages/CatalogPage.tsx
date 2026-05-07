/**
 * CatalogPage — DESIGN.md v3.0 §A (bucket entry-point) + §B (photo-top cards).
 *
 * v3.0 changes:
 *   - Reads `?bucket=people|animals|planet` from query string and threads it
 *     into the API call.
 *   - When `bucket` is present, page header swaps to bucket-specific title +
 *     subtitle.
 *   - Default sort changes to `largest_revenue` for bucket views (well-known
 *     orgs first), matching the donor's expectation when they click "People".
 *   - Catalog grid: 3-col desktop / 2-col tablet / 1-col mobile (CharityCard v3
 *     is photo-top, so wider cards work).
 */

import { useQuery } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"

import { CharityCard } from "@/components/charity/CharityCard"
import { api, type CharityListParams } from "@/lib/api"
import type { Bucket } from "@/types/api"

const VALID_BUCKETS: Bucket[] = ["people", "animals", "planet"]

function isBucket(value: string | null): value is Bucket {
  return value !== null && (VALID_BUCKETS as string[]).includes(value)
}

export function CatalogPage() {
  const { t } = useTranslation()
  const [searchParams, setSearchParams] = useSearchParams()

  const bucketParam = searchParams.get("bucket")
  const bucket: Bucket | undefined = isBucket(bucketParam) ? bucketParam : undefined

  const params: CharityListParams = {
    cause: searchParams.getAll("cause"),
    country: (searchParams.get("country") as CharityListParams["country"]) || undefined,
    size: (searchParams.get("size") as CharityListParams["size"]) || undefined,
    verification_status: (searchParams.get("verification_status") as CharityListParams["verification_status"]) || undefined,
    bucket,
    q: searchParams.get("q") || undefined,
    sort:
      (searchParams.get("sort") as CharityListParams["sort"]) ||
      (bucket ? "largest_revenue" : "most_recent_filing"),
    page: Number(searchParams.get("page") || 1),
  }

  const { data, isLoading, isError } = useQuery({
    queryKey: ["charities", params],
    queryFn: ({ signal }) => api.listCharities(params, { signal }),
  })

  const setFilter = (key: string, value: string | null) => {
    const next = new URLSearchParams(searchParams)
    if (value == null || value === "") next.delete(key)
    else next.set(key, value)
    next.delete("page")
    setSearchParams(next, { replace: true })
  }

  // Header content depends on whether a bucket filter is active.
  const headerTitle = bucket
    ? t(`bucket.${bucket}.pageTitle`)
    : t("catalog.title")
  const headerSubtitle = bucket ? t(`bucket.${bucket}.pageSubtitle`) : null

  return (
    <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12">
      <header className="mb-8">
        <h1 className="font-serif text-h1 font-semibold text-ink leading-tight">
          {headerTitle}
        </h1>
        {headerSubtitle && (
          <p className="text-body text-ink-2 mt-3 max-w-2xl">{headerSubtitle}</p>
        )}
        {data && (
          <p className="text-body-sm text-ink-3 mt-4">
            {t("catalog.showing", {
              from: (data.page - 1) * data.page_size + 1,
              to: Math.min(data.page * data.page_size, data.count),
              count: data.count,
            })}
          </p>
        )}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-8">
        <aside className="lg:sticky lg:top-20 lg:self-start">
          <div className="bg-surface border border-rule rounded-md p-5 space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-h4 font-semibold text-ink">{t("catalog.filters")}</h2>
              <button
                type="button"
                onClick={() => {
                  // Reset preserves the bucket filter (bucket is a *page mode*, not a filter).
                  const next = new URLSearchParams()
                  if (bucket) next.set("bucket", bucket)
                  setSearchParams(next, { replace: true })
                }}
                className="text-body-sm text-ink-3 hover:text-ink underline"
              >
                {t("catalog.reset")}
              </button>
            </div>

            <FilterGroup label={t("catalog.country")}>
              {(["US", "GB", "RU"] as const).map((c) => (
                <label key={c} className="flex items-center gap-2 text-body-sm text-ink py-1 cursor-pointer">
                  <input
                    type="radio"
                    name="country"
                    value={c}
                    checked={searchParams.get("country") === c}
                    onChange={(e) => setFilter("country", e.target.value)}
                    className="accent-verified"
                  />
                  {c === "US" ? "United States" : c === "GB" ? "United Kingdom" : "Russia"}
                </label>
              ))}
            </FilterGroup>

            <FilterGroup label={t("catalog.size")}>
              {(["small", "medium", "large"] as const).map((s) => (
                <label key={s} className="flex items-center gap-2 text-body-sm text-ink py-1 cursor-pointer">
                  <input
                    type="radio"
                    name="size"
                    value={s}
                    checked={searchParams.get("size") === s}
                    onChange={(e) => setFilter("size", e.target.value)}
                    className="accent-verified"
                  />
                  {s === "small" ? "<$100K" : s === "medium" ? "$100K–$1M" : ">$1M"}
                </label>
              ))}
            </FilterGroup>

            <FilterGroup label={t("catalog.verification")}>
              {(["verified", "listed", "stale"] as const).map((v) => (
                <label key={v} className="flex items-center gap-2 text-body-sm text-ink py-1 cursor-pointer">
                  <input
                    type="radio"
                    name="verification_status"
                    value={v}
                    checked={searchParams.get("verification_status") === v}
                    onChange={(e) => setFilter("verification_status", e.target.value)}
                    className="accent-verified"
                  />
                  {t(`charity.${v}`)}
                </label>
              ))}
            </FilterGroup>
          </div>
        </aside>

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

          {data && data.results.length === 0 && (
            <div className="border border-rule rounded-md p-12 text-center">
              <h2 className="text-h3 font-semibold text-ink mb-2">{t("catalog.noResults")}</h2>
              <p className="text-body text-ink-2">{t("catalog.tryRemoving")}</p>
            </div>
          )}

          {data && data.results.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {data.results.map((charity) => (
                <CharityCard key={charity.slug} charity={charity} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

function FilterGroup({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-body-sm font-semibold text-ink mb-2">{label}</h3>
      <div>{children}</div>
    </div>
  )
}
