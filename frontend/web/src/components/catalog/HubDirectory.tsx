/**
 * HubDirectory — the "Browse by" link block (v3.21).
 *
 * This is the entry point into every hub page: country, cause, registry. It sits
 * at the foot of the catalogue and of each hub page, so a crawler that lands
 * anywhere in the catalogue can reach all ~50 hubs in one hop, and every charity
 * in two.
 *
 * `activePath` marks the hub you're already on — it renders as plain text rather
 * than a self-link, so no page links to itself.
 */

import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { useHubs } from "@/lib/queries"
import { usePreferences } from "@/store/preferences"
import type { Hub } from "@/types/api"

function HubGroup({
  title,
  hubs,
  activePath,
  lang,
}: {
  title: string
  hubs: Hub[]
  activePath?: string
  lang: "en" | "ru"
}) {
  if (hubs.length === 0) return null
  return (
    <div>
      <h3 className="text-caption font-medium uppercase tracking-wide text-ink-3 mb-3">
        {title}
      </h3>
      <ul className="flex flex-wrap gap-x-4 gap-y-2">
        {hubs.map((hub) => {
          const label = hub.label[lang] || hub.label.en
          const isActive = hub.path === activePath
          return (
            <li key={hub.path} className="text-body-sm">
              {isActive ? (
                <span className="text-ink-3">
                  {label}
                  <span className="font-mono text-caption text-ink-3 ml-1.5">
                    {hub.count}
                  </span>
                </span>
              ) : (
                <Link
                  to={hub.path}
                  className="text-ink-2 hover:text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
                >
                  {label}
                  <span className="font-mono text-caption text-ink-3 ml-1.5">
                    {hub.count}
                  </span>
                </Link>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}

export function HubDirectory({ activePath }: { activePath?: string }) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const { data } = useHubs()

  if (!data) return null

  return (
    <section className="mt-16 pt-10 border-t border-rule">
      <h2 className="font-serif text-h3 font-semibold text-ink mb-2">
        {t("hubs.directoryTitle")}
      </h2>
      <p className="text-body-sm text-ink-2 mb-8 max-w-[65ch]">
        {t("hubs.directoryBody", { min: data.min_size })}
      </p>
      <div className="space-y-8">
        <HubGroup
          title={t("hubs.byRegistry")}
          hubs={data.registries}
          activePath={activePath}
          lang={lang}
        />
        <HubGroup
          title={t("hubs.byCountry")}
          hubs={data.countries}
          activePath={activePath}
          lang={lang}
        />
        <HubGroup
          title={t("hubs.byCause")}
          hubs={data.causes}
          activePath={activePath}
          lang={lang}
        />
      </div>
    </section>
  )
}
