/**
 * CharityCard v3 — photo-top product card per DESIGN.md v3.0 §B.
 *
 * v3.0 layout (replaces v2.0 bordered cream layout entirely):
 *   - TOP: 3:2 photo (uses charity.hero_photo_url; lazy-loaded).
 *     - Verified chip overlaid TOP-RIGHT (white pill, semi-transparent).
 *     - Empty-state: BrandedAvatar enlarged + neutral stone gradient.
 *   - BODY (white, p-5):
 *     - Logo (32px) + charity name (Source Serif h4)
 *     - Tagline (Inter body-sm, line-clamp-2)
 *     - Meta row: country · 1 cause-tag · "$X.XM revenue" (mono)
 *
 * Whole card is a wrapping <Link>. No separate "Open profile" button (v3.0 §B.4).
 * Hover: photo scale 1.03 + card shadow lift.
 */

import { HugeiconsIcon } from "@hugeicons/react"
import { Tick02Icon, Image01Icon } from "@hugeicons/core-free-icons"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { CharityLogo } from "@/components/charity/CharityLogo"
import { formatUsd } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"
import type { CharitySummary } from "@/types/api"

const COUNTRY_LABEL_EN: Record<string, string> = {
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
  const [photoErrored, setPhotoErrored] = useState(false)

  const name = charity.name[lang] || charity.name.en || charity.slug
  const tagline = charity.tagline[lang] || charity.tagline.en || ""
  const country =
    (lang === "ru" ? COUNTRY_LABEL_RU : COUNTRY_LABEL_EN)[charity.country] ?? charity.country
  const isVerified = charity.verification_status === "verified"
  const photoUrl = charity.hero_photo_url
  const showPhoto = photoUrl && !photoErrored

  const causeTag = charity.cause_tags.length > 0 ? charity.cause_tags[0] : null
  const revenueLabel =
    charity.total_revenue_usd != null
      ? formatUsd(charity.total_revenue_usd, { compact: true })
      : null

  return (
    <Link
      to={`/charities/${charity.slug}`}
      className="
        group block bg-surface-raised border border-rule rounded-md overflow-hidden
        transition-all duration-200 ease-out
        hover:border-ink-3 hover:shadow-md
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-verified focus-visible:ring-offset-2
      "
      aria-label={name}
    >
      {/* === Photo zone (top, 3:2) === */}
      <div className="relative aspect-[3/2] bg-stone-100 overflow-hidden">
        {showPhoto ? (
          <img
            src={photoUrl}
            alt=""
            loading="lazy"
            decoding="async"
            onError={() => setPhotoErrored(true)}
            className="
              h-full w-full object-cover object-center
              transition-transform duration-300 ease-out
              group-hover:scale-[1.03]
              motion-reduce:transition-none motion-reduce:group-hover:scale-100
            "
          />
        ) : (
          // Empty-state: warm-stone gradient + image-off icon. Card still scans.
          <div className="absolute inset-0 bg-gradient-to-br from-stone-200 to-stone-300 flex items-center justify-center">
            <HugeiconsIcon
              icon={Image01Icon}
              size={48}
              className="text-stone-400"
              aria-hidden="true"
            />
          </div>
        )}

        {/* Verified chip overlay — top-right */}
        {isVerified && (
          <span
            className="
              absolute top-3 right-3
              inline-flex items-center gap-1
              bg-white/95 backdrop-blur-sm
              rounded-full px-3 py-1
              text-caption font-medium text-verified
              shadow-sm
            "
            aria-label={t("charity.verified")}
          >
            <HugeiconsIcon icon={Tick02Icon} size={12} aria-hidden="true" />
            {t("charity.verified")}
          </span>
        )}
      </div>

      {/* === Body (white surface, p-5) === */}
      <div className="p-5">
        {/* Logo + name row */}
        <div className="flex items-center gap-3">
          <CharityLogo
            logoUrl={charity.logo_url}
            slug={charity.slug}
            name={name}
            size="sm"
          />
          <h3 className="font-serif text-h4 font-semibold text-ink leading-tight truncate min-w-0">
            {name}
          </h3>
        </div>

        {/* Tagline */}
        {tagline && (
          <p className="text-body-sm text-ink-2 mt-2 line-clamp-2">
            {tagline}
          </p>
        )}

        {/* Meta row */}
        <p className="mt-3 text-caption text-ink-3">
          <span>{country}</span>
          {causeTag && (
            <>
              <span className="mx-1.5">·</span>
              <span>{causeTag}</span>
            </>
          )}
          {revenueLabel && (
            <>
              <span className="mx-1.5">·</span>
              <span className="font-mono text-ink-2">{revenueLabel}</span>
            </>
          )}
        </p>
      </div>
    </Link>
  )
}
