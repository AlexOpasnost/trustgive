/**
 * CharityHubLinks — "this organisation also appears in" (v3.21).
 *
 * Renders the hub sections a charity belongs to: its country, the registry that
 * published its evidence, and each of its cause tags that has a hub.
 *
 * Purpose is twofold. For the reader it's the obvious next step from a profile —
 * other charities under the same regulator, or working on the same thing. For
 * the crawler it closes the loop: the catalogue links down to profiles, and each
 * profile links back up to its hubs, so no page in the catalogue sits at the end
 * of a one-way path.
 *
 * A hub is only shown if the backend published it (≥ the threshold in
 * `apps/charities/hubs.py`), which is why a Russian or Italian charity shows no
 * country link — those sections don't exist yet, and inventing a link to a
 * would-be page is how you get a soft 404.
 */

import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { useHubs } from "@/lib/queries"
import { usePreferences } from "@/store/preferences"
import type { Charity, Hub } from "@/types/api"

function hostOf(url: string): string {
  try {
    return new URL(url).hostname.toLowerCase().replace(/^www\./, "")
  } catch {
    return ""
  }
}

export function CharityHubLinks({ charity }: { charity: Charity }) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const { data: hubs } = useHubs()

  if (!hubs) return null

  const docHosts = new Set(
    charity.source_documents.map((doc) => hostOf(doc.url)).filter(Boolean),
  )

  const related: Hub[] = [
    ...hubs.registries.filter((h) => h.host && docHosts.has(h.host)),
    ...hubs.countries.filter((h) => h.code === charity.country),
    ...hubs.causes.filter((h) => charity.cause_tags.includes(h.slug)),
  ]

  if (related.length === 0) return null

  return (
    <section className="bg-surface-raised border-t border-rule">
      <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 band-tight">
        <h2 className="font-serif text-h2 font-semibold text-ink mb-4">
          {t("hubs.onProfileTitle")}
        </h2>
        <ul className="flex flex-wrap gap-x-4 gap-y-2 max-w-[720px]">
          {related.map((hub) => (
            <li key={hub.path} className="text-body-sm">
              <Link
                to={hub.path}
                className="text-ink-2 hover:text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
              >
                {hub.label[lang] || hub.label.en}
                <span className="font-mono text-caption text-ink-3 ml-1.5">
                  {hub.count}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
