/**
 * GuidePage — one evergreen guide, rendered from the block list in
 * `content/guides.ts`.
 *
 * Generic on purpose, unlike `ResearchArticlePage`, which dispatches on slug.
 * That is right for research — two findings with different arguments want
 * different shapes — and wrong here: ten how-to articles that each got their own
 * component would be ten places for the same layout to drift apart, and the
 * drift would show up as ten slightly different-looking pages on one site.
 *
 * `case` blocks are the reason these guides are worth reading rather than being
 * the same advice every charity site prints. Each one names something this
 * catalogue got wrong, with the identifier, what the registry actually answers,
 * and the finding that records how it was caught. Advice is cheap; a worked
 * example of the advice being ignored, by us, is not.
 */

import { ArrowLeft02Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"

import { GUIDES, GUIDE_CASES, type GuideBlock } from "@/content/guides"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
import { formatIsoDate } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"

function CaseBlock({ block, prose }: { block: Extract<GuideBlock, { kind: "case" }>; prose: string }) {
  const { t } = useTranslation()
  const detail = GUIDE_CASES[block.case]
  const identifier = "identifier" in detail ? detail.identifier : null
  const answer = "registryAnswer" in detail ? detail.registryAnswer : null
  const href = "href" in detail ? detail.href : null

  return (
    <aside className="bg-surface-raised border border-rule rounded-lg p-6 my-8">
      <p className="text-caption font-mono text-ink-3 mb-3">
        {t("guides.caseLabel")}
        <span className="mx-2">·</span>
        {t("guides.findingRef", { n: detail.finding })}
      </p>
      {identifier && answer && (
        <p className="text-body-sm font-mono text-ink mb-3">
          <span className="text-ink-3">{identifier}</span>
          <span className="mx-2 text-ink-3">→</span>
          {answer}
        </p>
      )}
      <p className="text-body text-ink-2 max-w-[65ch]">{prose}</p>
      {href && (
        <p className="mt-3">
          <a
            href={href}
            target="_blank"
            rel="noreferrer"
            className="text-body-sm text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("guides.checkItYourself")}
          </a>
        </p>
      )}
    </aside>
  )
}

export function GuidePage() {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const { slug = "" } = useParams<{ slug: string }>()

  const guide = GUIDES.find((g) => g.slug === slug)
  useDocumentTitle(guide ? t(`guides.articles.${slug}.title`) : t("guides.unknownTitle"))

  if (!guide) {
    return (
      <div className="max-w-(--container-narrow) mx-auto px-6 band-state text-center">
        <h1 className="text-h2 font-semibold text-ink mb-3">{t("guides.unknownTitle")}</h1>
        <p className="text-body text-ink-2 mb-8 max-w-[60ch] mx-auto">{t("guides.unknownBody")}</p>
        <Link
          to="/guides"
          className="inline-flex items-center gap-2 text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
        >
          <HugeiconsIcon icon={ArrowLeft02Icon} size={14} aria-hidden="true" />
          {t("guides.backToIndex")}
        </Link>
      </div>
    )
  }

  const base = `guides.articles.${slug}`

  return (
    <article className="max-w-(--container-narrow) mx-auto px-6 lg:px-12 band">
      <Link
        to="/guides"
        className="inline-flex items-center gap-2 text-body-sm text-ink-3 hover:text-ink mb-8"
      >
        <HugeiconsIcon icon={ArrowLeft02Icon} size={16} aria-hidden="true" />
        {t("guides.backToIndex")}
      </Link>

      <header>
        <p className="text-caption text-ink-3 font-mono mb-3">
          {t("guides.reviewed", { date: formatIsoDate(guide.reviewed, lang) })}
          <span className="mx-2">·</span>
          {t("guides.minutes", { count: guide.minutes })}
        </p>
        <h1 className="font-serif text-display font-bold text-ink mb-6">{t(`${base}.title`)}</h1>
        <p className="text-lead text-ink-2">{t(`${base}.standfirst`)}</p>
      </header>

      <hr className="border-rule my-12" />

      <div className="space-y-6">
        {guide.body.map((block, i) => {
          const key = `${base}.${block.key}`
          switch (block.kind) {
            case "heading":
              return (
                <h2
                  key={i}
                  className="font-serif text-h2 font-semibold text-ink leading-tight pt-6"
                >
                  {t(`${key}Title`)}
                </h2>
              )
            case "para":
              return (
                <p key={i} className="text-body text-ink-2 max-w-[65ch]">
                  {t(key)}
                </p>
              )
            case "list":
              return (
                <ul key={i} className="list-disc pl-6 space-y-2 max-w-[65ch]">
                  {Array.from({ length: block.count }, (_, n) => (
                    <li key={n} className="text-body text-ink-2">
                      {t(`${key}.${n}`)}
                    </li>
                  ))}
                </ul>
              )
            case "steps":
              return (
                <ol key={i} className="list-decimal pl-6 space-y-3 max-w-[65ch]">
                  {Array.from({ length: block.count }, (_, n) => (
                    <li key={n} className="text-body text-ink-2">
                      {t(`${key}.${n}`)}
                    </li>
                  ))}
                </ol>
              )
            case "caution":
              return (
                <p
                  key={i}
                  className="text-body text-ink-2 max-w-[65ch] border-l-2 border-rule pl-5 italic"
                >
                  {t(key)}
                </p>
              )
            case "case":
              return <CaseBlock key={i} block={block} prose={t(key)} />
            case "faq":
              return (
                <dl key={i} className="space-y-6 max-w-[65ch]">
                  {Array.from({ length: block.count }, (_, n) => (
                    <div key={n}>
                      <dt className="text-body font-semibold text-ink mb-2">
                        {t(`${key}.${n}.q`)}
                      </dt>
                      <dd className="text-body text-ink-2">{t(`${key}.${n}.a`)}</dd>
                    </div>
                  ))}
                </dl>
              )
          }
        })}
      </div>

      <hr className="border-rule my-12" />

      <p className="text-body-sm text-ink-3 max-w-[65ch]">{t("guides.footnote")}</p>
    </article>
  )
}
