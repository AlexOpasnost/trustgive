import { HugeiconsIcon } from "@hugeicons/react"
import { ArrowRight01Icon } from "@hugeicons/core-free-icons"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import type { CharitySummary } from "@/types/api"
import { formatPercent, formatUsd } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"

import { VerificationBadge } from "./VerificationBadge"

const COUNTRY_LABEL: Record<string, string> = {
  US: "United States",
  GB: "United Kingdom",
  RU: "Russia",
}

type Props = {
  charity: CharitySummary
}

export function CharityCard({ charity }: Props) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const name = charity.name[lang] || charity.name.en || charity.slug
  const tagline = charity.tagline[lang] || charity.tagline.en || ""

  const programPctClass =
    charity.program_expense_pct == null
      ? "text-ink-3"
      : Number(charity.program_expense_pct) < 50
        ? "text-error"
        : Number(charity.program_expense_pct) < 70
          ? "text-warning"
          : "text-ink-2"

  return (
    <Link
      to={`/charities/${charity.slug}`}
      className="block bg-surface border-b border-rule px-6 py-5 hover:bg-paper transition-colors group"
    >
      <div className="flex items-start gap-4">
        {charity.logo_url ? (
          <img
            src={charity.logo_url}
            alt=""
            className="w-12 h-12 rounded-md object-cover flex-shrink-0"
            loading="lazy"
          />
        ) : (
          <div className="w-12 h-12 rounded-md bg-info-soft text-info flex items-center justify-center font-semibold flex-shrink-0">
            {name.slice(0, 1).toUpperCase()}
          </div>
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-3">
            <h3 className="text-h3 font-semibold text-ink truncate">{name}</h3>
            <VerificationBadge status={charity.verification_status} size="sm" />
          </div>

          {tagline && <p className="text-body-sm text-ink-2 mt-1">{tagline}</p>}

          <p className="text-body-sm text-ink-2 mt-1">
            {COUNTRY_LABEL[charity.country] ?? charity.country}
            {charity.cause_tags.length > 0 && (
              <>
                <span className="mx-1">·</span>
                {charity.cause_tags.slice(0, 3).join(", ")}
              </>
            )}
          </p>

          <hr className="my-3 border-rule" />

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-body-sm">
            <span className="text-ink-2">
              {formatUsd(charity.total_revenue_usd, { compact: true })}
            </span>
            <span className={programPctClass}>
              {formatPercent(charity.program_expense_pct)} {t("charity.programs").toLowerCase()}
            </span>
            {charity.last_filed_date && (
              <span className="text-ink-3">filed {charity.last_filed_date.slice(0, 7)}</span>
            )}
          </div>

          {charity.trust_badges.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {charity.trust_badges.slice(0, 3).map((badge) => (
                <span
                  key={badge.slug}
                  className="text-caption text-ink-2 border border-rule rounded-sm px-2 py-0.5"
                >
                  {badge.label[lang] || badge.label.en}
                </span>
              ))}
            </div>
          )}
        </div>

        <span className="self-end text-body-sm text-ink-3 inline-flex items-center gap-1 group-hover:text-ink">
          {t("catalog.view")}
          <HugeiconsIcon icon={ArrowRight01Icon} size={14} />
        </span>
      </div>
    </Link>
  )
}
