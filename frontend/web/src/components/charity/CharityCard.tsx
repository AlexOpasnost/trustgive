/**
 * CharityCard v2 — bordered product card per DESIGN.md v2.0 §A.
 *
 * Layout zones:
 *   - Left:    logo (48px desktop / 40px mobile)
 *   - Centre:  identity (name, tagline, geo + meta line, trust badges)
 *   - Right:   numeric anchor (program-pct mono-figure with bar) + secondary CTA
 *
 * Empty-state (§A.2 fallback 2 / §F.4): when program_expense_pct is NULL but
 * total_revenue_usd is present, the right-anchor switches to revenue with the
 * caption "annual revenue" / "Годовая выручка". Card never renders "0% to programs"
 * because that would be a lie.
 *
 * Interactivity:
 *   - Whole card is a wrapping <Link> for keyboard / SR navigation.
 *   - The visible "Open profile" button is decorative (pointer-events-none) so
 *     clicks bubble to the wrapper. This avoids nested-interactive a11y issues.
 */

import { ArrowRight01Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/Button"
import { CharityLogo } from "@/components/charity/CharityLogo"
import { VerificationBadge } from "@/components/charity/VerificationBadge"
import { formatPercent, formatUsd } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"
import type { CharitySummary } from "@/types/api"

const COUNTRY_LABEL: Record<string, string> = {
  US: "United States",
  GB: "United Kingdom",
  RU: "Russia",
}
const COUNTRY_LABEL_RU: Record<string, string> = {
  US: "США",
  GB: "Великобритания",
  RU: "Россия",
}

type Props = {
  charity: CharitySummary
}

export function CharityCard({ charity }: Props) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)

  const name = charity.name[lang] || charity.name.en || charity.slug
  const tagline = charity.tagline[lang] || charity.tagline.en || ""
  const country =
    (lang === "ru" ? COUNTRY_LABEL_RU : COUNTRY_LABEL)[charity.country] ?? charity.country

  const hasProgramPct =
    charity.program_expense_pct != null && Number.isFinite(Number(charity.program_expense_pct))
  const hasRevenue = charity.total_revenue_usd != null

  // Right-anchor selection per §A.2 fallback chain.
  let anchorFigure: string | null = null
  let anchorCaption: string | null = null
  let anchorBarPct: number | null = null
  if (hasProgramPct) {
    const pct = Number(charity.program_expense_pct)
    anchorFigure = formatPercent(pct)
    anchorCaption = t("card.programs")
    anchorBarPct = Math.min(Math.max(pct, 0), 100)
  } else if (hasRevenue) {
    anchorFigure = formatUsd(charity.total_revenue_usd, { compact: true })
    anchorCaption = t("card.annualRevenue")
    anchorBarPct = null
  }

  return (
    <Link
      to={`/charities/${charity.slug}`}
      className="group block bg-surface border border-rule rounded-md transition-colors hover:border-ink-3 active:bg-paper focus-visible:outline-none focus-visible:border-ink-3"
      aria-label={`${name} — ${t("card.openProfile")}`}
    >
      <div className="flex items-start gap-4 p-5 sm:gap-5 sm:p-6">
        {/* Logo zone (left) */}
        <div className="flex-shrink-0">
          <div className="hidden sm:block">
            <CharityLogo logoUrl={charity.logo_url} slug={charity.slug} name={name} size="md" />
          </div>
          <div className="sm:hidden">
            <CharityLogo logoUrl={charity.logo_url} slug={charity.slug} name={name} size="sm" />
          </div>
        </div>

        {/* Identity zone (centre) */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-3">
            <h3 className="text-h4 sm:text-h3 font-semibold text-ink leading-tight line-clamp-2 sm:truncate">
              {name}
            </h3>
            <div className="hidden sm:block flex-shrink-0">
              <VerificationBadge status={charity.verification_status} size="sm" />
            </div>
          </div>

          <div className="sm:hidden mt-1">
            <VerificationBadge status={charity.verification_status} size="sm" />
          </div>

          {tagline && (
            <p className="text-body-sm text-ink-2 mt-1 line-clamp-2">{tagline}</p>
          )}

          <hr className="my-3 border-rule" />

          <p className="text-body-sm text-ink-2">
            {country}
            {charity.cause_tags.length > 0 && (
              <>
                <span className="mx-1.5 text-ink-3">·</span>
                <span>{charity.cause_tags.slice(0, 2).join(", ")}</span>
              </>
            )}
          </p>

          {charity.trust_badges.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {charity.trust_badges.slice(0, 3).map((badge) => (
                <span
                  key={badge.slug}
                  className="text-caption text-ink-2 border border-rule rounded-sm px-2 py-0.5 bg-surface-raised"
                >
                  {badge.label[lang] || badge.label.en}
                </span>
              ))}
              {charity.trust_badges.length > 3 && (
                <span className="text-caption text-ink-3 px-2 py-0.5">
                  +{charity.trust_badges.length - 3}
                </span>
              )}
            </div>
          )}

          {/* Mobile: anchor + CTA stack below the centre column */}
          <div className="sm:hidden mt-4 space-y-3">
            {anchorFigure && (
              <div>
                <div className="font-mono text-h3 text-ink leading-none">{anchorFigure}</div>
                <div className="text-caption text-ink-3 mt-1">{anchorCaption}</div>
                {anchorBarPct != null && (
                  <div
                    className="h-1 bg-rule rounded-sm mt-2 overflow-hidden w-32"
                    aria-hidden="true"
                  >
                    <div
                      className="h-full bg-ink-2"
                      style={{ width: `${anchorBarPct}%` }}
                    />
                  </div>
                )}
              </div>
            )}
            <Button
              as="a"
              variant="secondary"
              size="sm"
              className="w-full pointer-events-none group-hover:bg-ink group-hover:text-paper group-hover:border-ink"
              tabIndex={-1}
            >
              {t("card.openProfile")}
              <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
            </Button>
          </div>
        </div>

        {/* Anchor + CTA zone (right, desktop only) */}
        <div className="hidden sm:flex flex-col items-end justify-between flex-shrink-0 self-stretch w-[150px] gap-4">
          {anchorFigure ? (
            <div className="text-right">
              <div className="font-mono text-h2 text-ink leading-none">{anchorFigure}</div>
              <div className="text-caption text-ink-3 mt-1.5">{anchorCaption}</div>
              {anchorBarPct != null ? (
                <div
                  className="h-1 bg-rule rounded-sm mt-2 ml-auto w-16 overflow-hidden"
                  aria-hidden="true"
                >
                  <div
                    className="h-full bg-ink-2"
                    style={{ width: `${anchorBarPct}%` }}
                  />
                </div>
              ) : (
                <div
                  className="h-px bg-rule mt-3 ml-auto w-16"
                  aria-hidden="true"
                />
              )}
            </div>
          ) : (
            <div className="text-right">
              <div className="text-caption text-ink-3">
                {t("card.regCountry", { country })}
              </div>
            </div>
          )}

          <Button
            as="a"
            variant="secondary"
            size="sm"
            className="pointer-events-none group-hover:bg-ink group-hover:text-paper group-hover:border-ink"
            tabIndex={-1}
          >
            {t("card.openProfile")}
            <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
          </Button>
        </div>
      </div>
    </Link>
  )
}
