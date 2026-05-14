/**
 * MoneyBreakdown — financial-allocation chart on the detail page.
 *
 * Per DESIGN.md v2.0 §F.3 ("Only total revenue available"), when the only
 * populated field is total_revenue_usd (program/admin/fundraising all NULL),
 * the bar chart is replaced with a single mono-figure block + honesty paragraph.
 * The honesty paragraph is positioning-as-UX: "we don't infer what wasn't disclosed".
 */

import { useTranslation } from "react-i18next"

import type { MoneyBreakdown as MoneyBreakdownType } from "@/types/api"
import { formatPercent, formatUsd } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"

type Props = {
  /** Full Form-990 breakdown. Pass null/undefined for the §F.3 empty-state. */
  data?: MoneyBreakdownType | null
  /** Total revenue (used for §F.3 fallback when `data` is missing/empty). */
  totalRevenueUsd?: number | string | null
  /** Fiscal year for the empty-state caption. */
  fallbackYear?: number | null
}

export function MoneyBreakdown({ data, totalRevenueUsd, fallbackYear }: Props) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)

  const hasLines = Boolean(data && data.lines && data.lines.length > 0)

  // §F.3 empty-state: only total revenue available.
  if (!hasLines) {
    if (totalRevenueUsd == null) return null
    const year = data?.year ?? fallbackYear

    return (
      <section className="bg-surface border border-rule rounded-md p-6">
        <header className="mb-6">
          {/* h3, not h2 — this card sits inside the page's "Where the money
              goes" <h2> section, so its own heading is a level down. */}
          <h3 className="text-h2 font-semibold text-ink">{t("detail.moneyBreakdown")}</h3>
          {year && (
            <p className="text-body-sm text-ink-3 mt-1">{t("charity.fiscalYear", { year })}</p>
          )}
        </header>

        <div className="flex items-baseline gap-3 mb-4">
          <span className="font-mono text-h1 text-ink leading-none">
            {formatUsd(totalRevenueUsd, { compact: true })}
          </span>
          <span className="text-body-sm text-ink-3">{t("card.annualRevenue").toLowerCase()}</span>
        </div>

        <hr className="border-rule my-5" />

        <p className="text-body-sm text-ink-2 max-w-[65ch]">
          {t("detail.breakdown.unavailable")}
        </p>
      </section>
    )
  }

  const breakdown = data as MoneyBreakdownType

  return (
    <section className="bg-surface border border-rule rounded-md p-6">
      <header className="mb-4">
        {/* h3 — nested under the page's "Where the money goes" <h2>. */}
        <h3 className="text-h2 font-semibold text-ink">{t("detail.moneyBreakdown")}</h3>
        <p className="text-body-sm text-ink-3 mt-1">
          {t("charity.fiscalYear", { year: breakdown.year })}
        </p>
      </header>

      <div className="space-y-4">
        {breakdown.lines.map((line) => {
          const label = line.label[lang] || line.label.en
          const widthPct = Math.min(Math.max(Number(line.percent), 0), 100)
          return (
            <div key={label}>
              <div className="flex items-baseline justify-between mb-1">
                <span className="text-body font-medium text-ink">{label}</span>
                <span className="font-mono text-body text-ink">
                  {formatPercent(line.percent)}
                </span>
              </div>
              <div className="h-2 bg-rule rounded-sm overflow-hidden" aria-hidden="true">
                <div className="h-full bg-ink-2" style={{ width: `${widthPct}%` }} />
              </div>
              <div className="text-body-sm text-ink-3 font-mono mt-1">
                {formatUsd(line.amount_usd, { compact: true })}
              </div>
            </div>
          )
        })}
      </div>

      {breakdown.source_label && (
        <p className="text-caption text-ink-3 mt-6 font-mono">
          Source: {breakdown.source_label}
        </p>
      )}
    </section>
  )
}
