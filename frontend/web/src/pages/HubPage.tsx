/**
 * HubPage — one crawlable section of the catalogue (v3.21).
 *
 * Serves three routes with the same body:
 *   /charities/country/{code}    e.g. /charities/country/us
 *   /charities/cause/{slug}      e.g. /charities/cause/global-health
 *   /charities/registry/{slug}   e.g. /charities/registry/irs-990
 *
 * A hub only exists if the backend published it (`GET /api/hubs/`, threshold in
 * `apps/charities/hubs.py`). An unlisted slug renders "no such section" rather
 * than an empty grid — a page that promises "charities in X" and shows nothing
 * is exactly the thin content Google declines to index, and it would be a false
 * claim about X besides.
 */

import { ArrowLeft02Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useTranslation } from "react-i18next"
import { Link, useParams, useSearchParams } from "react-router-dom"

import { CatalogResults } from "@/components/catalog/CatalogResults"
import { HubDirectory } from "@/components/catalog/HubDirectory"
import type { CharityListParams } from "@/lib/api"
import { useHubs } from "@/lib/queries"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
import { usePreferences } from "@/store/preferences"
import type { Hub, HubKind } from "@/types/api"

/** Filters that select exactly the charities a hub claims to hold. */
function hubParams(hub: Hub): Omit<CharityListParams, "page" | "page_size"> {
  const base = { sort: "alphabetical" as const }
  if (hub.kind === "country") return { ...base, country: hub.code }
  if (hub.kind === "cause") return { ...base, cause: [hub.slug] }
  return { ...base, registry: hub.slug }
}

export function HubPage({ kind }: { kind: HubKind }) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const { slug = "" } = useParams<{ slug: string }>()
  const [searchParams] = useSearchParams()
  const { data: hubs, isLoading } = useHubs()

  const page = Math.max(1, Number(searchParams.get("page")) || 1)

  const group =
    kind === "country"
      ? hubs?.countries
      : kind === "cause"
        ? hubs?.causes
        : hubs?.registries
  const hub = group?.find((h) => h.slug === slug.toLowerCase())

  const label = hub ? hub.label[lang] || hub.label.en : ""
  const heading = hub ? t(`hubs.heading.${kind}`, { label }) : ""
  useDocumentTitle(hub ? heading : isLoading ? null : t("hubs.unknownTitle"))

  if (!hubs && isLoading) {
    return (
      <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 band-tight">
        <div className="skeleton h-9 w-1/2 mb-4" />
        <div className="skeleton h-4 w-2/3" />
      </div>
    )
  }

  if (!hub) {
    return (
      <div className="max-w-(--container-narrow) mx-auto px-6 band-state text-center">
        <h1 className="text-h2 font-semibold text-ink mb-3">
          {t("hubs.unknownTitle")}
        </h1>
        <p className="text-body text-ink-2 mb-8 max-w-[60ch] mx-auto">
          {t("hubs.unknownBody", { min: hubs?.min_size ?? 5 })}
        </p>
        <Link
          to="/charities"
          className="inline-flex items-center gap-2 text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
        >
          <HugeiconsIcon icon={ArrowLeft02Icon} size={14} aria-hidden="true" />
          {t("hubs.backToCatalog")}
        </Link>
      </div>
    )
  }

  const intro =
    hub.kind === "registry" && hub.description
      ? hub.description[lang] || hub.description.en
      : t(`hubs.intro.${hub.kind}`, { label, count: hub.count })

  return (
    <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 band-tight">
      {/* Breadcrumb — gives the crawler the parent relationship and the reader
          a way back that isn't the browser button. */}
      <nav className="mb-6 text-body-sm text-ink-3" aria-label={t("hubs.breadcrumb")}>
        <Link
          to="/charities"
          className="hover:text-ink underline decoration-rule decoration-1 underline-offset-4"
        >
          {t("catalog.title")}
        </Link>
        <span className="mx-2">/</span>
        <span>{t(`hubs.byKind.${hub.kind}`)}</span>
        <span className="mx-2">/</span>
        <span className="text-ink-2">{label}</span>
      </nav>

      <header className="mb-8">
        <h1 className="font-serif text-h1 font-semibold text-ink leading-tight">
          {heading}
        </h1>
        <p className="text-body text-ink-2 mt-3 max-w-[65ch]">{intro}</p>
        {hub.kind === "registry" && hub.publisher && (
          <p className="text-body-sm text-ink-3 mt-2">
            {t("hubs.publisher", { publisher: hub.publisher })}
          </p>
        )}
      </header>

      <main>
        <CatalogResults
          params={hubParams(hub)}
          page={page}
          buildPageHref={(p) => (p <= 1 ? hub.path : `${hub.path}?page=${p}`)}
          empty={{
            title: t("catalog.noResults"),
            body: t("catalog.tryRemoving"),
          }}
        />
      </main>

      <HubDirectory activePath={hub.path} />
    </div>
  )
}
