/**
 * DataSourcesPage — one section per register, including what each one can't do.
 *
 * This is the page a researcher or journalist checks before citing anything, so
 * it carries the limits as prominently as the coverage. Canada is listed as
 * absent with the reason, because a source page that only describes what worked
 * is marketing.
 */

import { useTranslation } from "react-i18next"

import { useDocumentTitle } from "@/lib/useDocumentTitle"

type Source = {
  key: string
  href: string
}

const SOURCES: Source[] = [
  { key: "propublica", href: "https://projects.propublica.org/nonprofits/api" },
  { key: "charityCommission", href: "https://register-of-charities.charitycommission.gov.uk/" },
  { key: "acnc", href: "https://www.acnc.gov.au/charity/charities" },
  { key: "minjust", href: "https://unro.minjust.gov.ru/NKOs.aspx" },
]

export function DataSourcesPage() {
  const { t } = useTranslation()
  useDocumentTitle(t("sources.title"))

  return (
    <article className="max-w-(--container-narrow) mx-auto px-6 lg:px-12 py-16 lg:py-24">
      <header>
        <h1
          className="font-serif text-ink mb-6"
          style={{ fontSize: "clamp(34px, 4.5vw, 52px)", lineHeight: 1.1, fontWeight: 700, letterSpacing: "-0.02em" }}
        >
          {t("sources.title")}
        </h1>
        <p className="text-body text-ink-2" style={{ fontSize: "20px", lineHeight: "34px" }}>
          {t("sources.lead")}
        </p>
      </header>

      <hr className="border-rule my-12" />

      <section className="mb-12">
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">{t("sources.howTitle")}</h2>
        <p className="text-body leading-relaxed text-ink-2" style={{ fontSize: "19px", lineHeight: "32px" }}>
          {t("sources.howBody")}
        </p>
      </section>

      {SOURCES.map((source) => (
        <div key={source.key}>
          <hr className="border-rule my-12" />
          <section>
            <h2 className="text-h2 font-semibold text-ink mb-2 font-sans">
              {t(`sources.${source.key}.name`)}
            </h2>
            <p className="text-caption text-ink-3 font-mono mb-4">
              {t(`sources.${source.key}.meta`)}
            </p>
            <p className="text-body leading-relaxed text-ink-2" style={{ fontSize: "19px", lineHeight: "32px" }}>
              {t(`sources.${source.key}.body`)}
            </p>
            <p className="text-body-sm text-ink-2 mt-4 border-l-2 border-rule pl-4">
              <span className="text-ink-3">{t("sources.limitLabel")} </span>
              {t(`sources.${source.key}.limit`)}
            </p>
            <p className="mt-4">
              <a
                href={source.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
              >
                {t("sources.visit")}
              </a>
            </p>
          </section>
        </div>
      ))}

      <hr className="border-rule my-12" />

      {/* Absence, stated as plainly as presence. */}
      <section>
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">{t("sources.missingTitle")}</h2>
        <p className="text-body leading-relaxed text-ink-2" style={{ fontSize: "19px", lineHeight: "32px" }}>
          {t("sources.missingBody")}
        </p>
        <ul
          className="mt-6 space-y-3 list-disc list-inside text-body text-ink-2 font-sans"
          style={{ fontSize: "17px", lineHeight: "28px" }}
        >
          <li>{t("sources.missingCanada")}</li>
          <li>{t("sources.missingEurope")}</li>
        </ul>
      </section>

      <hr className="border-rule my-12" />

      <section>
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">{t("sources.useTitle")}</h2>
        <p className="text-body leading-relaxed text-ink-2" style={{ fontSize: "19px", lineHeight: "32px" }}>
          {t("sources.useBody")}
        </p>
        <p className="mt-6">
          <a
            href="https://api.trustgive.org/api/docs/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("sources.apiLink")}
          </a>
        </p>
      </section>
    </article>
  )
}
