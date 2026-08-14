/**
 * GuidesPage — the index of evergreen guides.
 *
 * Shows the date each guide was last *reviewed against its sources*, not the
 * date it was written. For a how-to about reading registers, "written in 2026"
 * says nothing a reader needs; "checked against the register on this date" is
 * the claim that matters, and it is the same claim the rest of the site makes
 * about every charity in the catalogue.
 */

import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { GUIDES } from "@/content/guides"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
import { formatIsoDate } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"

export function GuidesPage() {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  useDocumentTitle(t("guides.title"))

  return (
    <article className="max-w-(--container-narrow) mx-auto px-6 lg:px-12 band">
      <header>
        <h1 className="font-serif text-display font-bold text-ink mb-6">{t("guides.title")}</h1>
        <p className="text-lead text-ink-2">{t("guides.lead")}</p>
      </header>

      <hr className="border-rule my-12" />

      <ul className="space-y-10">
        {GUIDES.map((guide) => (
          <li key={guide.slug}>
            <p className="text-caption text-ink-3 font-mono mb-2">
              {t("guides.reviewed", { date: formatIsoDate(guide.reviewed, lang) })}
              <span className="mx-2">·</span>
              {t("guides.minutes", { count: guide.minutes })}
            </p>
            <h2 className="font-serif text-h2 font-semibold text-ink leading-tight mb-3">
              <Link
                to={`/guides/${guide.slug}`}
                className="underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
              >
                {t(`guides.articles.${guide.slug}.title`)}
              </Link>
            </h2>
            <p className="text-body text-ink-2 max-w-[65ch]">
              {t(`guides.articles.${guide.slug}.standfirst`)}
            </p>
          </li>
        ))}
      </ul>

      <hr className="border-rule my-12" />

      <p className="text-body-sm text-ink-3 max-w-[65ch]">{t("guides.footnote")}</p>
    </article>
  )
}
