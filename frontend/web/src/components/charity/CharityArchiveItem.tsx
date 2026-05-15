/**
 * CharityArchiveItem — DESIGN_v4.md §6.2 catalog entry.
 *
 * Replaces the v3 CharityCard inside /charities. Pure editorial archive item:
 * no border, no card, no shadow. Photo column (4:3) sits beside a text column
 * (serif name + italic standfirst + Inter byline). Hairline rules between
 * items are drawn by the parent — this component just renders its own row.
 *
 * Layout breakpoints:
 *   - ≥lg (1024+): 5/12 photo + 7/12 text, side by side
 *   - <lg: photo stacks above text, both full-width
 *
 * Verified-state signalling: no chip. The byline carries the structural
 * cue — `EIN/Reg ... · $X revenue · Last filed 2024`. When source-document
 * filing info is available (detail page only, Phase 4) the byline upgrades
 * to `Form 990 · 2024 · via ProPublica`. For the catalog list-row we keep
 * it lighter: country, lead cause, revenue, last filed.
 */

import { useState } from "react"
import { Link } from "react-router-dom"

import { countryLabel } from "@/lib/countryLabels"
import {
  PHOTO_WIDTHS,
  SRCSET_WIDTHS,
  buildSrcSet,
  wikimediaThumb,
} from "@/lib/image"
import { formatUsd } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"
import type { CharitySummary } from "@/types/api"

type Props = {
  charity: CharitySummary
}

export function CharityArchiveItem({ charity }: Props) {
  const lang = usePreferences((s) => s.lang)
  const [photoErrored, setPhotoErrored] = useState(false)

  const name = charity.name[lang] || charity.name.en || charity.slug
  const tagline = charity.tagline[lang] || charity.tagline.en || ""
  const country = countryLabel(charity.country, lang)

  const photoUrl = wikimediaThumb(charity.hero_photo_url, PHOTO_WIDTHS.card)
  const photoSrcSet = buildSrcSet(charity.hero_photo_url, SRCSET_WIDTHS.card)
  const showPhoto = photoUrl && !photoErrored

  const causeTag = charity.cause_tags[0] ?? null
  const revenueLabel =
    charity.total_revenue_usd != null
      ? formatUsd(charity.total_revenue_usd, { compact: true })
      : null
  const filedYear = charity.last_filed_date
    ? charity.last_filed_date.slice(0, 4)
    : null

  // Byline parts joined by " · ". Drop falsy entries so we don't render
  // double separators when a field is missing.
  const bylineParts = [
    country,
    causeTag,
    revenueLabel ? `${revenueLabel} revenue` : null,
    filedYear ? `Filed ${filedYear}` : null,
  ].filter(Boolean) as string[]

  return (
    <Link
      to={`/charities/${charity.slug}`}
      aria-label={name}
      className="
        block group
        focus-visible:outline-none focus-visible:ring-1
      "
      style={
        {
          ["--tw-ring-color" as never]: "var(--color-link)",
        } as never
      }
    >
      <article
        className="
          grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-10
          py-8 lg:py-10
        "
      >
        {/* Photo (left on desktop, top on mobile per user's mobile decision). */}
        <div className="lg:col-span-5">
          <div
            className="relative aspect-[4/3] overflow-hidden"
            style={{ background: "var(--color-paper-2-v4)" }}
          >
            {showPhoto ? (
              <img
                src={photoUrl}
                {...(photoSrcSet ? { srcSet: photoSrcSet } : {})}
                sizes="(min-width: 1024px) 40vw, 92vw"
                alt=""
                loading="lazy"
                decoding="async"
                crossOrigin="anonymous"
                onError={() => setPhotoErrored(true)}
                className="
                  absolute inset-0 h-full w-full object-cover object-center
                  transition-opacity duration-300 ease-out
                  group-hover:opacity-90
                  motion-reduce:transition-none
                "
              />
            ) : (
              // No card-chrome empty state — just an empty paper-2 swatch.
              // The hairline rule and the byline carry the row.
              <div aria-hidden="true" className="absolute inset-0" />
            )}
          </div>
        </div>

        {/* Text column. */}
        <div className="lg:col-span-7 flex flex-col justify-center">
          {/* Eyebrow: country, all caps Inter */}
          <p
            className="font-sans uppercase mb-3"
            style={{
              fontSize: "var(--text-ui-sm)",
              lineHeight: "var(--text-ui-sm--line-height)",
              letterSpacing: "0.14em",
              color: "var(--color-ink-3-v4)",
              fontWeight: 500,
            }}
          >
            {country}
            {charity.bucket && (
              <>
                <span className="mx-2">·</span>
                <span>
                  {charity.bucket === "people"
                    ? lang === "ru"
                      ? "Людям"
                      : "People"
                    : charity.bucket === "planet"
                      ? lang === "ru"
                        ? "Планете"
                        : "Planet"
                      : lang === "ru"
                        ? "Животным"
                        : "Animals"}
                </span>
              </>
            )}
          </p>

          {/* Name — serif heading-lg */}
          <h3
            className="font-serif mb-3 max-w-[28ch] group-hover:underline decoration-1 underline-offset-4"
            style={{
              fontSize: "var(--text-heading-lg)",
              lineHeight: "var(--text-heading-lg--line-height)",
              fontWeight: 600,
              color: "var(--color-ink-v4)",
            }}
          >
            {name}
          </h3>

          {/* Tagline — italic serif standfirst */}
          {tagline && (
            <p
              className="font-serif italic mb-5 max-w-[52ch]"
              style={{
                fontSize: "var(--text-body-v4)",
                lineHeight: "var(--text-body-v4--line-height)",
                color: "var(--color-ink-2-v4)",
              }}
            >
              {tagline}
            </p>
          )}

          {/* Byline — Inter, tabular metadata. Mono is reserved for the
              registration-ID prefix to read like a citation slug. */}
          <p
            className="font-sans"
            style={{
              fontSize: "var(--text-ui-sm)",
              lineHeight: "var(--text-ui-sm--line-height)",
              color: "var(--color-ink-3-v4)",
            }}
          >
            {charity.registration_id && (
              <>
                <span className="font-mono" style={{ color: "var(--color-ink-2-v4)" }}>
                  {charity.country === "US"
                    ? "EIN"
                    : charity.country === "GB"
                      ? "CC"
                      : "Reg"}{" "}
                  {charity.registration_id}
                </span>
                {bylineParts.length > 0 && <span className="mx-2">·</span>}
              </>
            )}
            {bylineParts.join(" · ")}
          </p>
        </div>
      </article>
    </Link>
  )
}
