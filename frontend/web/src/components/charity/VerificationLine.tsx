/**
 * VerificationLine — the single most important element on a charity page
 * (STRATEGY.md §5.2).
 *
 *   Verified · IRS Form 990 · fiscal year ending 31 December 2023 ·
 *   re-checked 30 July 2026        → Open the filing
 *
 * Before this, a page said only "Verified" in a green pill and put the evidence
 * behind a click, below a photograph that filled 70% of the screen. The badge
 * was the claim and the document was the footnote — the wrong way round for a
 * product whose entire argument is "don't trust us, read the file".
 *
 * Every clause is dropped rather than faked when its fact is missing: no filing
 * date, no "fiscal year ending" clause. The document type comes from the
 * document's `kind` rather than its free-text label, because labels already
 * carry the year ("IRS Form 990 (FY 2023)") and would print it twice.
 *
 * A charity with no source document renders the honest negative instead. The
 * public catalogue is verified-only today, so that path is unreachable through
 * the API — it stays because the rule is that trust state is never blank
 * (v3.18), and because the filter is one line in views.py away from changing.
 */

import { ArrowRight01Icon, Tick02Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useTranslation } from "react-i18next"

import { formatIsoDate } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"
import type { Charity, SourceDocument } from "@/types/api"

export function VerificationLine({
  charity,
  onOpenFiling,
}: {
  charity: Charity
  /** Opens the source-document drawer, which shows context before sending the
   *  reader to a third-party site. */
  onOpenFiling: (doc: SourceDocument) => void
}) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)

  const filing = charity.source_documents.find((doc) => doc.url)
  const isVerified = charity.verification_status === "verified" && Boolean(filing)

  if (!isVerified || !filing) {
    return (
      <p className="text-body-sm text-ink-2 mt-3 max-w-[65ch]">
        <span className="font-medium text-ink-3">{t("charity.notVerified")}</span>
        <span className="mx-2 text-ink-3">·</span>
        {t("charity.notVerifiedNote")}
      </p>
    )
  }

  const periodEnd = formatIsoDate(charity.last_filed_date, lang)
  const reChecked = formatIsoDate(charity.data_freshness?.last_synced_at, lang)
  const kindLabel = t(`charity.docKind.${filing.kind}`, {
    defaultValue: filing.source_label || filing.label[lang] || filing.label.en,
  })

  const clauses = [kindLabel]
  if (periodEnd) clauses.push(t("charity.fiscalYearEnding", { date: periodEnd }))
  if (reChecked) clauses.push(t("charity.lastChecked", { date: reChecked }))

  return (
    <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-2">
      <span className="inline-flex items-center gap-1.5 bg-verified-soft text-verified text-body-sm font-medium rounded-full px-3 py-1">
        <HugeiconsIcon icon={Tick02Icon} size={14} aria-hidden="true" />
        {t("charity.verified")}
      </span>

      <span className="text-body-sm text-ink-2">
        {clauses.map((clause, i) => (
          <span key={clause}>
            {i > 0 && <span className="mx-2 text-ink-3">·</span>}
            {clause}
          </span>
        ))}
      </span>

      <button
        type="button"
        onClick={() => onOpenFiling(filing)}
        className="inline-flex items-center gap-1.5 text-body-sm font-medium text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
      >
        {t("charity.openFiling")}
        <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
      </button>
    </div>
  )
}
