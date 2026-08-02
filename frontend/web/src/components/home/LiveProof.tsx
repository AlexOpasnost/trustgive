/**
 * LiveProof — one real verification, on the homepage (STRATEGY.md §4.2).
 *
 * The homepage claimed "every charity here links to the regulator's own filing"
 * and then showed three photographs. The single block that separates this
 * product from every competitor — an actual government document, one click away
 * — was nowhere above the fold. This is that block.
 *
 * Everything in it is read from the live API at render time: the name, the
 * registration number, the document's own label, the fiscal period it covers,
 * and the URL. Nothing is written into the markup. That is deliberate — a
 * hardcoded "Registration 208625442" would be a fact the page asserts without
 * reading it back from the source, which is exactly the defect class
 * DATA_INTEGRITY.md §1 and §5 were written about.
 *
 * If the fetch fails, or the charity carries no source document with a URL, the
 * block renders nothing. A proof block that can't show its proof has no business
 * being on the page.
 */

import { ArrowRight01Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useQuery } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { api } from "@/lib/api"
import { useStats } from "@/lib/queries"
import { formatIsoDate } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"

/**
 * The worked example. GiveWell is the right pick: it is the organisation a
 * sceptical reader is most likely to already know, its EIN was re-derived and
 * confirmed against ProPublica in the v3.18 audit, and its filing is a PDF the
 * reader can actually open rather than a JavaScript registry shell.
 */
const PROOF_SLUG = "givewell"

export function LiveProof() {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)

  const { data: stats } = useStats()

  const { data: charity } = useQuery({
    queryKey: ["charity", PROOF_SLUG],
    queryFn: ({ signal }) => api.getCharity(PROOF_SLUG, { signal }),
    staleTime: 60 * 60 * 1000,
    retry: 1,
  })

  if (!charity) return null

  const filing = charity.source_documents.find((doc) => doc.url)
  if (!filing) return null

  const name = charity.name[lang] || charity.name.en || charity.slug
  // Document *type*, not the document's own label: labels already carry the
  // year ("IRS Form 990 (FY 2023)") and the sentence states the period itself.
  const filingLabel = t(`charity.docKind.${filing.kind}`, {
    defaultValue: filing.label[lang] || filing.label.en || filing.source_label,
  })
  const periodEnd = formatIsoDate(charity.last_filed_date, lang)

  return (
    <section className="bg-surface-raised border-b border-rule">
      <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12 lg:py-16">
        <p className="text-caption uppercase tracking-widest text-ink-3 font-medium mb-5">
          {t("home.proof.eyebrow")}
        </p>

        <div className="border border-rule rounded-md p-6 lg:p-8 max-w-[760px]">
          <p className="text-body text-ink" style={{ fontSize: "19px", lineHeight: "32px" }}>
            {t("home.proof.lead", { name })}{" "}
            <span className="font-mono text-ink-2">{charity.registration_id}</span>
            {". "}
            {periodEnd
              ? t("home.proof.filing", { document: filingLabel, date: periodEnd })
              : t("home.proof.filingNoDate", { document: filingLabel })}
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3">
            {/* Straight to the regulator's document — not to a page about it.
                That one hop is the entire product claim, so it is the primary
                action here. */}
            <a
              href={filing.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-body font-medium text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
            >
              {t("home.proof.openFiling")}
              <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
            </a>
            <Link
              to={`/charities/${charity.slug}`}
              className="text-body-sm text-ink-2 hover:text-ink underline decoration-rule decoration-1 underline-offset-4"
            >
              {t("home.proof.seeProfile", { name })}
            </Link>
          </div>
        </div>

        {/* The catalogue size is read, not written. This sentence carried a
            hardcoded "370" for exactly as long as it took to notice — the same
            defect as the homepage's "27 countries". */}
        <p className="text-body-sm text-ink-3 mt-5 max-w-[65ch]">
          {stats
            ? t("home.proof.footnote", { count: stats.charities })
            : t("home.proof.footnoteNoCount")}
        </p>
      </div>
    </section>
  )
}
