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

import { useQuery } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"

import { CharityCard } from "@/components/charity/CharityCard"
import { Chip } from "@/components/ui/Chip"
import { api, type CharityListParams } from "@/lib/api"
import { BUCKET_SUBFILTERS, COUNTRY_FILTERS } from "@/lib/buckets"
import { usePreferences } from "@/store/preferences"
import type { Bucket } from "@/types/api"

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
  const activeCountry = searchParams.get("country")

  const params: CharityListParams = {
    cause: activeCause ? [activeCause] : [],
    country: (activeCountry as CharityListParams["country"]) || undefined,
    bucket,
    sort: bucket ? "largest_revenue" : "most_recent_filing",
    page: Number(searchParams.get("page") || 1),
    // Render the full catalog without paginate-controls UI. Catalog tops
    // out at ~100 charities for the foreseeable future; bumping this is
    // simpler than building "Load more" / pagination links.
    page_size: 200,
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

      {/* === Country chips === */}
      <div className="flex flex-wrap gap-2 mb-3" role="group" aria-label={t("catalog.country")}>
        {COUNTRY_FILTERS.map((c) => {
          const active = (activeCountry ?? null) === c.code
          return (
            <Chip
              key={c.code ?? "all"}
              active={active}
              onClick={() => setFilter("country", c.code)}
            >
              {lang === "ru" ? c.labelRu : c.labelEn}
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

        {data && data.results.length === 0 && (
          <div className="border border-rule rounded-md p-12 text-center">
            <h2 className="text-h3 font-semibold text-ink mb-2">
              {t("catalog.noResults")}
            </h2>
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
  )
}
