import { useQuery } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"

import { CharityCard } from "@/components/charity/CharityCard"
import { api, type CharityListParams } from "@/lib/api"

export function CatalogPage() {
  const { t } = useTranslation()
  const [searchParams, setSearchParams] = useSearchParams()

  const params: CharityListParams = {
    cause: searchParams.getAll("cause"),
    country: (searchParams.get("country") as CharityListParams["country"]) || undefined,
    size: (searchParams.get("size") as CharityListParams["size"]) || undefined,
    verification_status: (searchParams.get("verification_status") as CharityListParams["verification_status"]) || undefined,
    q: searchParams.get("q") || undefined,
    sort: (searchParams.get("sort") as CharityListParams["sort"]) || "most_recent_filing",
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

  return (
    <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12">
      <header className="mb-8">
        <h1 className="text-h1 font-semibold text-ink">{t("catalog.title")}</h1>
        {data && (
          <p className="text-body-sm text-ink-3 mt-2">
            {t("catalog.showing", {
              from: (data.page - 1) * data.page_size + 1,
              to: Math.min(data.page * data.page_size, data.count),
              count: data.count,
            })}
          </p>
        )}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-8">
        <aside className="lg:sticky lg:top-20 lg:self-start">
          <div className="bg-surface border border-rule rounded-md p-5 space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-h4 font-semibold text-ink">{t("catalog.filters")}</h2>
              <button
                type="button"
                onClick={() => setSearchParams({}, { replace: true })}
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
            <div className="space-y-2">
              {[0, 1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-surface border-b border-rule px-6 py-5">
                  <div className="skeleton h-5 w-2/3 mb-2" />
                  <div className="skeleton h-4 w-1/2 mb-3" />
                  <div className="skeleton h-4 w-3/4" />
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
            <div className="bg-surface border-t border-rule">
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
