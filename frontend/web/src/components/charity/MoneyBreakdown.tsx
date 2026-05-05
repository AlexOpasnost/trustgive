import { useTranslation } from "react-i18next"

import type { MoneyBreakdown as MoneyBreakdownType } from "@/types/api"
import { formatPercent, formatUsd } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"

type Props = {
  data: MoneyBreakdownType
}

export function MoneyBreakdown({ data }: Props) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)

  return (
    <section className="bg-surface border border-rule rounded-md p-6">
      <header className="mb-4">
        <h2 className="text-h2 font-semibold text-ink">{t("charity.moneyGoes")}</h2>
        <p className="text-body-sm text-ink-3 mt-1">{t("charity.fiscalYear", { year: data.year })}</p>
      </header>

      <div className="space-y-4">
        {data.lines.map((line) => {
          const label = line.label[lang] || line.label.en
          const widthPct = Math.min(Math.max(Number(line.percent), 0), 100)
          return (
            <div key={label}>
              <div className="flex items-baseline justify-between mb-1">
                <span className="text-body font-medium text-ink">{label}</span>
                <span className="font-mono text-body text-ink">{formatPercent(line.percent)}</span>
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

      {data.source_label && (
        <p className="text-caption text-ink-3 mt-6 font-mono">Source: {data.source_label}</p>
      )}
    </section>
  )
}
