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
 *
 * v3.21 (crawlability):
 *   - Grid, counts and "Load more" moved into <CatalogResults>, shared with the
 *     hub pages, and joined by numbered `?page=N` links. Before this, 310 of 370
 *     charities had no internal link pointing at them and Search Console filed
 *     them as "Discovered — currently not indexed".
 *   - <HubDirectory> at the foot links every country / cause / registry section.
 *   - A failed search now says what an empty catalogue actually means here
 *     (unconfirmed organisations aren't published) instead of the generic
 *     "no charities match these filters".
 */

import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"

import { CatalogResults } from "@/components/catalog/CatalogResults"
import { HubDirectory } from "@/components/catalog/HubDirectory"
import { Chip } from "@/components/ui/Chip"
import { type CharityListParams } from "@/lib/api"
import { BUCKET_SUBFILTERS, REGION_FILTERS } from "@/lib/buckets"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
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
  // v3.7: replaced single-country filter with regional groups
  // (?region=europe → country=GB,DE,NL,CH,SE,FR). Frontend-only param;
  // translated to comma-separated ISO codes for the backend BaseInFilter.
  const activeRegion = searchParams.get("region")
  const region = REGION_FILTERS.find((r) => r.slug === activeRegion)
  const countryParam = region?.countries?.length ? region.countries.join(",") : undefined

  // Free-text query. Backed by Postgres FTS + pg_trgm on the server, so it
  // tolerates a misremembered name and matches on registration number too —
  // which is the point: the common arrival is "someone named a charity at me,
  // is it real?", not "show me charities by cause".
  const query = (searchParams.get("q") || "").trim()

  const page = Math.max(1, Number(searchParams.get("page")) || 1)

  const baseParams: Omit<CharityListParams, "page" | "page_size"> = {
    cause: activeCause ? [activeCause] : [],
    country: countryParam,
    bucket,
    q: query || undefined,
    // Relevance ordering is the server's default when q is present; imposing a
    // filing-date sort on top of it would bury the best match.
    sort: query ? undefined : bucket ? "largest_revenue" : "most_recent_filing",
  }

  const setFilter = (key: string, value: string | null) => {
    const next = new URLSearchParams(searchParams)
    if (value == null || value === "") next.delete(key)
    else next.set(key, value)
    next.delete("page")
    setSearchParams(next, { replace: true })
  }

  /** Page link that keeps every active filter. Page 1 drops `?page` so the
   *  first page has exactly one URL rather than two that duplicate each other. */
  const buildPageHref = (target: number) => {
    const next = new URLSearchParams(searchParams)
    if (target <= 1) next.delete("page")
    else next.set("page", String(target))
    const qs = next.toString()
    return qs ? `/charities?${qs}` : "/charities"
  }

  const headerTitle = query
    ? t("search.resultsFor", { query })
    : bucket
      ? t(`bucket.${bucket}.pageTitle`)
      : t("catalog.title")
  const headerSubtitle = !query && bucket ? t(`bucket.${bucket}.pageSubtitle`) : null
  useDocumentTitle(headerTitle)

  const subfilters = bucket ? BUCKET_SUBFILTERS[bucket] : null

  // A search that finds nothing means something specific on this site, and it
  // isn't "try another filter": the catalogue publishes only organisations whose
  // regulator filing we could open, so an absent charity may well be real.
  const empty = query
    ? {
        title: t("search.noMatch", { query }),
        body: t("search.noMatchBody"),
      }
    : { title: t("catalog.noResults"), body: t("catalog.tryRemoving") }

  return (
    <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12">
      <header className="mb-8">
        <h1 className="font-serif text-h1 font-semibold text-ink leading-tight">
          {headerTitle}
        </h1>
        {headerSubtitle && (
          <p className="text-body text-ink-2 mt-3 max-w-2xl">{headerSubtitle}</p>
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
        <CatalogResults
          params={baseParams}
          page={page}
          buildPageHref={buildPageHref}
          empty={empty}
        />
      </main>

      <HubDirectory />
    </div>
  )
}
