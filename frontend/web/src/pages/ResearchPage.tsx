/**
 * ResearchPage — the index of published findings (STRATEGY Block D).
 *
 * The section exists because of STRATEGY §12's central argument: product
 * announcements have not brought this project a single external link, and they
 * won't. What earns a citation is a finding someone else needs to reference.
 * The raw material is already here — auditing this catalogue produced results
 * that hold outside it.
 *
 * The index deliberately shows publication dates and reading times: a research
 * page with undated entries reads as marketing.
 */

import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { RESEARCH_ARTICLES } from "@/content/research"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
import { formatIsoDate } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"

export function ResearchPage() {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  useDocumentTitle(t("research.title"))

  return (
    <article className="max-w-(--container-narrow) mx-auto px-6 lg:px-12 py-16 lg:py-24">
      <header>
        <h1
          className="font-serif text-ink mb-6"
          style={{
            fontSize: "clamp(34px, 4.5vw, 52px)",
            lineHeight: 1.1,
            fontWeight: 700,
            letterSpacing: "-0.02em",
          }}
        >
          {t("research.title")}
        </h1>
        <p className="text-body text-ink-2" style={{ fontSize: "20px", lineHeight: "34px" }}>
          {t("research.lead")}
        </p>
      </header>

      <hr className="border-rule my-12" />

      <ul className="space-y-10">
        {RESEARCH_ARTICLES.map((article) => {
          const published = formatIsoDate(article.published, lang)
          return (
            <li key={article.slug}>
              <p className="text-caption text-ink-3 font-mono mb-2">
                {published}
                <span className="mx-2">·</span>
                {t("research.minutes", { count: article.minutes })}
              </p>
              <h2 className="font-serif text-h2 font-semibold text-ink leading-tight mb-3">
                <Link
                  to={`/research/${article.slug}`}
                  className="underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
                >
                  {t(`research.articles.${article.slug}.title`)}
                </Link>
              </h2>
              <p className="text-body text-ink-2 max-w-[65ch]">
                {t(`research.articles.${article.slug}.standfirst`)}
              </p>
            </li>
          )
        })}
      </ul>

      <hr className="border-rule my-12" />

      <p className="text-body-sm text-ink-3 max-w-[65ch]">{t("research.footnote")}</p>
    </article>
  )
}
