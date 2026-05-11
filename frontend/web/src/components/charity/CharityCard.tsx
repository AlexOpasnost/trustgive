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
import { PHOTO_WIDTHS, wikimediaThumb } from "@/lib/image"
import { formatUsd } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"
import type { CharitySummary } from "@/types/api"

// v3.14: extended to all 27 countries in the catalog so cards don't show
// raw ISO codes ("DE·...") for non-US/UK/RU entries. Keep in sync with
// Country enum in apps/charities/models.py.
const COUNTRY_LABEL_EN: Record<string, string> = {
  // Anglosphere + RU
  US: "United States", GB: "United Kingdom", RU: "Russia",
  CA: "Canada", AU: "Australia", NZ: "New Zealand",
  // Continental Europe
  DE: "Germany", NL: "Netherlands", CH: "Switzerland", SE: "Sweden",
  FR: "France", IT: "Italy", ES: "Spain", IE: "Ireland", NO: "Norway",
  BE: "Belgium", DK: "Denmark", PL: "Poland", FI: "Finland", AT: "Austria",
  // Asia
  JP: "Japan", SG: "Singapore", IN: "India", PH: "Philippines",
  ID: "Indonesia", VN: "Vietnam", TH: "Thailand", BD: "Bangladesh",
  // Africa
  KE: "Kenya", ZA: "South Africa", GH: "Ghana", MZ: "Mozambique",
  LS: "Lesotho", SN: "Senegal", TZ: "Tanzania", UG: "Uganda",
  // Latin America
  BR: "Brazil", AR: "Argentina", CL: "Chile", CO: "Colombia",
  MX: "Mexico", EC: "Ecuador", CR: "Costa Rica", PE: "Peru",
  // MENA
  LB: "Lebanon", EG: "Egypt", JO: "Jordan", TN: "Tunisia", IL: "Israel",
}
const COUNTRY_LABEL_RU: Record<string, string> = {
  US: "США", GB: "Великобритания", RU: "Россия",
  CA: "Канада", AU: "Австралия", NZ: "Новая Зеландия",
  DE: "Германия", NL: "Нидерланды", CH: "Швейцария", SE: "Швеция",
  FR: "Франция", IT: "Италия", ES: "Испания", IE: "Ирландия", NO: "Норвегия",
  BE: "Бельгия", DK: "Дания", PL: "Польша", FI: "Финляндия", AT: "Австрия",
  JP: "Япония", SG: "Сингапур", IN: "Индия", PH: "Филиппины",
  ID: "Индонезия", VN: "Вьетнам", TH: "Таиланд", BD: "Бангладеш",
  KE: "Кения", ZA: "ЮАР", GH: "Гана", MZ: "Мозамбик",
  LS: "Лесото", SN: "Сенегал", TZ: "Танзания", UG: "Уганда",
  BR: "Бразилия", AR: "Аргентина", CL: "Чили", CO: "Колумбия",
  MX: "Мексика", EC: "Эквадор", CR: "Коста-Рика", PE: "Перу",
  LB: "Ливан", EG: "Египет", JO: "Иордания", TN: "Тунис", IL: "Израиль",
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
  const photoUrl = wikimediaThumb(charity.hero_photo_url, PHOTO_WIDTHS.card)
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
            crossOrigin="anonymous"
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
