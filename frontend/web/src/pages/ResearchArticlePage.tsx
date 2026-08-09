/**
 * ResearchArticlePage — one published finding.
 *
 * Dispatches on slug rather than rendering a generic article shape: there is
 * one piece so far, its structure is specific to what it argues, and inventing a
 * CMS for a single document would be the wrong kind of work. When a second
 * article arrives with a different shape, it gets its own component here.
 *
 * Numbers come from `content/research.ts` — frozen, with the date they were
 * measured — not from the live API. A research finding is a snapshot; one whose
 * figures shift under the reader is not citable.
 */

import { ArrowLeft02Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"

import {
  FILING_AGE,
  FILING_AGE_BUCKETS,
  HEADLINE,
  RESEARCH_ARTICLES,
  VERIFICATION_BY_COUNTRY,
} from "@/content/research"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
import { formatIsoDate } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"

const COUNTRY_NAME: Record<string, { en: string; ru: string }> = {
  US: { en: "United States", ru: "США" },
  GB: { en: "United Kingdom", ru: "Великобритания" },
  CA: { en: "Canada", ru: "Канада" },
  AU: { en: "Australia", ru: "Австралия" },
  IT: { en: "Italy", ru: "Италия" },
  ES: { en: "Spain", ru: "Испания" },
  DE: { en: "Germany", ru: "Германия" },
  NL: { en: "Netherlands", ru: "Нидерланды" },
  NZ: { en: "New Zealand", ru: "Новая Зеландия" },
  FR: { en: "France", ru: "Франция" },
  IE: { en: "Ireland", ru: "Ирландия" },
  NO: { en: "Norway", ru: "Норвегия" },
  BE: { en: "Belgium", ru: "Бельгия" },
  DK: { en: "Denmark", ru: "Дания" },
}

export function ResearchArticlePage() {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const { slug = "" } = useParams<{ slug: string }>()

  const article = RESEARCH_ARTICLES.find((a) => a.slug === slug)
  useDocumentTitle(article ? t(`research.articles.${slug}.title`) : t("research.unknownTitle"))

  if (!article) {
    return (
      <div className="max-w-(--container-narrow) mx-auto px-6 band-state text-center">
        <h1 className="text-h2 font-semibold text-ink mb-3">{t("research.unknownTitle")}</h1>
        <p className="text-body text-ink-2 mb-8 max-w-[60ch] mx-auto">
          {t("research.unknownBody")}
        </p>
        <Link
          to="/research"
          className="inline-flex items-center gap-2 text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
        >
          <HugeiconsIcon icon={ArrowLeft02Icon} size={14} aria-hidden="true" />
          {t("research.backToIndex")}
        </Link>
      </div>
    )
  }

  const key = `research.articles.${slug}`
  const published = formatIsoDate(article.published, lang)

  return (
    <article className="max-w-(--container-narrow) mx-auto px-6 lg:px-12 band">
      <Link
        to="/research"
        className="inline-flex items-center gap-2 text-body-sm text-ink-3 hover:text-ink mb-8"
      >
        <HugeiconsIcon icon={ArrowLeft02Icon} size={16} aria-hidden="true" />
        {t("research.backToIndex")}
      </Link>

      <header>
        <p className="text-caption text-ink-3 font-mono mb-3">
          {published}
          <span className="mx-2">·</span>
          {t("research.minutes", { count: article.minutes })}
        </p>
        <h1 className="font-serif text-display font-bold text-ink mb-6">{t(`${key}.title`)}</h1>
        <p className="text-lead text-ink-2">{t(`${key}.standfirst`)}</p>
      </header>

      <hr className="border-rule my-12" />

      {slug === "what-we-could-not-verify" ? (
        <CoverageArticle lang={lang} />
      ) : (
        <FreshnessArticle lang={lang} />
      )}

      <hr className="border-rule my-12" />

      <Section title={t("research.methodTitle")}>
        <P className="text-ink-3">{t(`${key}.method`, { date: published })}</P>
        <p className="mt-6 flex flex-wrap gap-x-6 gap-y-2">
          <a
            href="https://github.com/AlexOpasnost/trustgive/blob/main/backend/research_query.py"
            target="_blank"
            rel="noopener noreferrer"
            className="text-body-sm text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("research.linkScript")}
          </a>
          <Link
            to="/api"
            className="text-body-sm text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("research.linkApi")}
          </Link>
          <Link
            to="/data-sources"
            className="text-body-sm text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("research.linkSources")}
          </Link>
        </p>
      </Section>
    </article>
  )
}

/** "A third of the charities we assembled could not be verified." */
function CoverageArticle({ lang }: { lang: "en" | "ru" }) {
  const { t } = useTranslation()
  const key = "research.articles.what-we-could-not-verify"
  return (
    <>
      <Section title={t(`${key}.s1Title`)}>
        <P>{t(`${key}.s1p1`, { assembled: HEADLINE.assembled, verified: HEADLINE.verified })}</P>
        <P className="mt-4">{t(`${key}.s1p2`, { unverified: HEADLINE.unverified })}</P>
      </Section>

      <Section title={t(`${key}.s2Title`)} className="mt-12">
        <P>
          {t(`${key}.s2p1`, {
            noDocument: HEADLINE.noDocumentAtAll,
            unverified: HEADLINE.unverified,
            deadLink: HEADLINE.deadLink,
          })}
        </P>
        <P className="mt-4">{t(`${key}.s2p2`)}</P>
      </Section>

      <Section title={t(`${key}.s3Title`)} className="mt-12">
        <P>{t(`${key}.s3p1`)}</P>
        <CountryTable lang={lang} />
        <P className="mt-6">{t(`${key}.s3p2`)}</P>
      </Section>

      <Section title={t(`${key}.s4Title`)} className="mt-12">
        <P>{t(`${key}.s4p1`, { tested: HEADLINE.canadaTested })}</P>
        <P className="mt-4">{t(`${key}.s4p2`)}</P>
        <P className="mt-4">
          {t(`${key}.s4p3`, {
            genuine: HEADLINE.canadaGenuine,
            wrongEntity: HEADLINE.canadaWrongEntity,
            unresolvable: HEADLINE.canadaUnresolvable,
            tested: HEADLINE.canadaTested,
          })}
        </P>
      </Section>

      <Section title={t(`${key}.s5Title`)} className="mt-12">
        <P>{t(`${key}.s5p1`)}</P>
        <P className="mt-4">{t(`${key}.s5p2`)}</P>
      </Section>
    </>
  )
}

/** "Nobody has current financial data on a charity." */
function FreshnessArticle({ lang }: { lang: "en" | "ru" }) {
  const { t } = useTranslation()
  const key = "research.articles.how-old-is-charity-financial-data"
  return (
    <>
      <Section title={t(`${key}.s1Title`)}>
        <P>{t(`${key}.s1p1`, { measured: FILING_AGE.measured })}</P>
        <P className="mt-4">{t(`${key}.s1p2`)}</P>
      </Section>

      <Section title={t(`${key}.s2Title`)} className="mt-12">
        <P>
          {t(`${key}.s2p1`, {
            median: FILING_AGE.medianMonths,
            older: FILING_AGE.olderThan24Months,
            measured: FILING_AGE.measured,
          })}
        </P>
        <AgeTable />
        <P className="mt-6">{t(`${key}.s2p2`)}</P>
      </Section>

      <Section title={t(`${key}.s3Title`)} className="mt-12">
        <P>{t(`${key}.s3p1`)}</P>
        <ul className="mt-4 space-y-2">
          {FILING_AGE.commonPeriodEnds.map((row) => (
            <li key={row.date} className="text-body-sm text-ink-2">
              <span className="font-mono text-ink">{row.date}</span>
              <span className="mx-2 text-ink-3">·</span>
              {t(`${key}.periodEndRow`, { count: row.count })}
            </li>
          ))}
        </ul>
        <P className="mt-6">{t(`${key}.s3p2`)}</P>
      </Section>

      <Section title={t(`${key}.s4Title`)} className="mt-12">
        <P>{t(`${key}.s4p1`)}</P>
        <ul className="mt-4 space-y-2">
          {FILING_AGE.byCountry.map((row) => (
            <li key={row.code} className="text-body-sm text-ink-2">
              <span className="text-ink">{COUNTRY_NAME[row.code]?.[lang] ?? row.code}</span>
              <span className="mx-2 text-ink-3">·</span>
              <span className="font-mono">
                {t(`${key}.medianMonths`, { count: row.median })}
              </span>
              <span className="mx-2 text-ink-3">·</span>
              <span className="text-ink-3">n={row.n}</span>
            </li>
          ))}
        </ul>
        <P className="mt-6">
          {t(`${key}.s4p2`, {
            gbMin: FILING_AGE.gbRangeMonths.min,
            gbMax: FILING_AGE.gbRangeMonths.max,
            usMax: FILING_AGE.usRangeMonths.max,
          })}
        </P>
      </Section>

      <Section title={t(`${key}.s5Title`)} className="mt-12">
        <P>{t(`${key}.s5p1`)}</P>
        <P className="mt-4">{t(`${key}.s5p2`)}</P>
      </Section>
    </>
  )
}

function AgeTable() {
  const { t } = useTranslation()
  const key = "research.articles.how-old-is-charity-financial-data"
  return (
    <div className="mt-6 overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-rule">
            <th className="py-2 pr-4 text-caption font-medium uppercase tracking-wide text-ink-3">
              {t(`${key}.colAge`)}
            </th>
            <th className="py-2 pr-4 text-caption font-medium uppercase tracking-wide text-ink-3 text-right">
              {t(`${key}.colCount`)}
            </th>
            <th className="py-2 text-caption font-medium uppercase tracking-wide text-ink-3 text-right">
              {t("research.colRate")}
            </th>
          </tr>
        </thead>
        <tbody>
          {FILING_AGE_BUCKETS.map((bucket) => {
            const share = (100 * bucket.count) / FILING_AGE.measured
            return (
              <tr key={bucket.key} className="border-b border-rule/60">
                <td className="py-2 pr-4 text-body-sm text-ink">
                  {t(`${key}.bucket.${bucket.key}`)}
                </td>
                <td className="py-2 pr-4 text-body-sm text-ink-2 text-right font-mono">
                  {bucket.count}
                </td>
                <td
                  className={`py-2 text-body-sm text-right font-mono ${
                    bucket.count === 0 ? "text-ink" : "text-ink-2"
                  }`}
                >
                  {share.toFixed(1)}%
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

function CountryTable({ lang }: { lang: "en" | "ru" }) {
  const { t } = useTranslation()
  return (
    <div className="mt-6 overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-rule">
            <th className="py-2 pr-4 text-caption font-medium uppercase tracking-wide text-ink-3">
              {t("research.colCountry")}
            </th>
            <th className="py-2 pr-4 text-caption font-medium uppercase tracking-wide text-ink-3 text-right">
              {t("research.colAssembled")}
            </th>
            <th className="py-2 pr-4 text-caption font-medium uppercase tracking-wide text-ink-3 text-right">
              {t("research.colVerified")}
            </th>
            <th className="py-2 text-caption font-medium uppercase tracking-wide text-ink-3 text-right">
              {t("research.colRate")}
            </th>
          </tr>
        </thead>
        <tbody>
          {VERIFICATION_BY_COUNTRY.map((row) => {
            const rate = Math.round((100 * row.verified) / row.assembled)
            return (
              <tr key={row.code} className="border-b border-rule/60">
                <td className="py-2 pr-4 text-body-sm text-ink">
                  {COUNTRY_NAME[row.code]?.[lang] ?? row.code}
                </td>
                <td className="py-2 pr-4 text-body-sm text-ink-2 text-right font-mono">
                  {row.assembled}
                </td>
                <td className="py-2 pr-4 text-body-sm text-ink-2 text-right font-mono">
                  {row.verified}
                </td>
                <td
                  className={`py-2 text-body-sm text-right font-mono ${
                    rate === 0 ? "text-ink" : "text-ink-2"
                  }`}
                >
                  {rate}%
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

function Section({
  title,
  children,
  className = "",
}: {
  title: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <section className={className}>
      <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">{title}</h2>
      {children}
    </section>
  )
}

function P({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <p className={`text-prose text-ink-2 ${className}`}>{children}</p>
  )
}
