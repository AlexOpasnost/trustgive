/**
 * CharityDetailPage — DESIGN.md v3.0 §C.
 *
 * v3.0 section order:
 *   1. Hero photo (full-bleed 70vh) with white name + tagline + verified chip
 *      + back link + photo credit overlaid (bottom 35% gradient).
 *      Fallback when no hero_photo_url: cream/serif title block, no photo.
 *   2. Identity strip — logo + name + EIN/Reg/Country/Founded · Last filed.
 *   3. About (description) — 65ch.
 *   4. Donate primary CTA (above expense breakdown, per user spec).
 *   5. Methodology (cream/serif secondary surface).
 *   6. Where the money goes (MoneyBreakdown component, kept).
 *   7. Source documents (drawer pattern, kept).
 *   8. Press mentions (kept).
 *
 * Compare CTA from v2.0 is REMOVED.
 */

import { ArrowLeft02Icon, ArrowRight01Icon, LinkSquare02Icon, Tick02Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"

import { CharityLogo } from "@/components/charity/CharityLogo"
import { DonateConfirmModal } from "@/components/charity/DonateConfirmModal"
import { MoneyBreakdown } from "@/components/charity/MoneyBreakdown"
import { SourceDocumentDrawer } from "@/components/charity/SourceDocumentDrawer"
import { Button } from "@/components/ui/Button"
import { api } from "@/lib/api"
import { PHOTO_WIDTHS, wikimediaThumb } from "@/lib/image"
import { usePreferences } from "@/store/preferences"
import type { Charity, SourceDocument } from "@/types/api"

export function CharityDetailPage() {
  const { slug = "" } = useParams<{ slug: string }>()
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const [openDoc, setOpenDoc] = useState<SourceDocument | null>(null)
  const [donateOpen, setDonateOpen] = useState(false)

  const { data: charity, isLoading, isError } = useQuery({
    queryKey: ["charity", slug],
    queryFn: ({ signal }) => api.getCharity(slug, { signal }),
    enabled: Boolean(slug),
  })

  if (isLoading) {
    return (
      <div>
        {/* Hero skeleton — same height as real hero to avoid CLS */}
        <div className="relative bg-stone-200 h-[55vh] md:h-[70vh] min-h-[360px]">
          <div className="absolute inset-0 skeleton" />
        </div>
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12">
          <div className="skeleton h-6 w-1/3 mb-6" />
          <div className="skeleton h-4 w-2/3 mb-2" />
          <div className="skeleton h-4 w-1/2 mb-8" />
          <div className="skeleton h-32 w-full max-w-[720px] mb-8" />
          <div className="skeleton h-12 w-64" />
        </div>
      </div>
    )
  }

  if (isError || !charity) {
    return (
      <div className="max-w-(--container-narrow) mx-auto px-6 py-24 text-center">
        <h1 className="text-h2 font-semibold text-ink mb-2">{t("common.error")}</h1>
        <p className="text-body text-ink-2">{t("common.errorBody")}</p>
      </div>
    )
  }

  const name = charity.name[lang] || charity.name.en || charity.slug
  const tagline = charity.tagline[lang] || charity.tagline.en
  const description = charity.description[lang] || charity.description.en
  const methodology = charity.methodology_note[lang] || charity.methodology_note.en
  const donationHost = (() => {
    try {
      return new URL(charity.donation_url).hostname.replace(/^www\./, "")
    } catch {
      return charity.donation_url
    }
  })()

  return (
    <div>
      {/* === HERO === */}
      <DetailHero charity={charity} name={name} tagline={tagline ?? ""} />

      {/* === IDENTITY STRIP (white surface, below hero) === */}
      <section className="bg-surface-raised border-b border-rule">
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-8">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex items-center gap-4 min-w-0">
              <CharityLogo
                logoUrl={charity.logo_url}
                slug={charity.slug}
                name={name}
                size="lg"
              />
              <div className="min-w-0">
                <h2 className="text-h3 font-semibold text-ink leading-tight truncate">
                  {name}
                </h2>
                <p className="text-body-sm text-ink-2 mt-1">
                  <span className="font-mono">EIN/Reg {charity.registration_id}</span>
                  <span className="mx-2 text-ink-3">·</span>
                  <span>{charity.country}</span>
                  {charity.founded_year && (
                    <>
                      <span className="mx-2 text-ink-3">·</span>
                      <span>Founded {charity.founded_year}</span>
                    </>
                  )}
                </p>
              </div>
            </div>
            {charity.last_filed_date && (
              <p className="text-caption text-ink-3 font-mono">
                Last filed {charity.last_filed_date}
              </p>
            )}
          </div>
        </div>
      </section>

      {/* === ABOUT === */}
      {description && (
        <section className="bg-surface-raised">
          <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 pt-12 lg:pt-16">
            <h2 className="font-serif text-h2 font-semibold text-ink mb-4">
              {t("detail.about")}
            </h2>
            <p className="text-body text-ink-2 leading-relaxed max-w-[65ch]">
              {description}
            </p>
          </div>
        </section>
      )}

      {/* === STALE-DATA WARNING === */}
      {charity.is_stale && charity.last_filed_date && (
        <div className="bg-surface-raised">
          <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 mt-8">
            <div
              className="bg-warning-soft border-l-4 border-warning px-4 py-3 rounded-md max-w-[720px]"
              role="status"
            >
              <p className="text-body-sm text-warning">
                {t("charity.staleWarning", { date: charity.last_filed_date })}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* === DONATE CTA (above the money breakdown) === */}
      {charity.donation_url && (
        <section className="bg-surface-raised">
          <div className="max-w-[560px] mx-auto px-6 my-12 lg:my-16 text-center">
            <Button
              variant="primary"
              size="lg"
              className="w-full"
              onClick={() => setDonateOpen(true)}
            >
              {t("detail.donate.cta", { hostname: donationHost })}
              <HugeiconsIcon icon={ArrowRight01Icon} size={16} aria-hidden="true" />
            </Button>
            <p className="text-caption text-ink-3 mt-3">
              {t("detail.donate.microcopy")}
            </p>
          </div>
        </section>
      )}

      {/* === METHODOLOGY (cream/serif secondary surface) === */}
      {methodology && (
        <section className="bg-paper border-y border-rule">
          <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12 lg:py-16">
            <h2 className="font-serif text-h2 font-semibold text-ink mb-4">
              {t("detail.methodology")}
            </h2>
            <p
              className="font-serif text-ink-2 max-w-[65ch] italic"
              style={{ fontSize: "18px", lineHeight: "30px" }}
            >
              {methodology}
            </p>
          </div>
        </section>
      )}

      {/* === WHERE THE MONEY GOES === */}
      <section className="bg-surface-raised">
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12 lg:py-16">
          <h2 className="font-serif text-h2 font-semibold text-ink mb-6">
            {t("charity.moneyGoes")}
          </h2>
          <div className="max-w-[720px]">
            <MoneyBreakdown
              data={charity.money_breakdown}
              totalRevenueUsd={charity.total_revenue_usd}
              fallbackYear={charity.last_filed_date ? Number(charity.last_filed_date.slice(0, 4)) : null}
            />
          </div>
        </div>
      </section>

      {/* === SOURCE DOCUMENTS === */}
      {charity.source_documents.length > 0 && (
        <section className="bg-surface-raised border-t border-rule">
          <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12 lg:py-16">
            <h2 className="font-serif text-h2 font-semibold text-ink mb-6">
              {t("charity.sourceDocuments")}
            </h2>
            <ul className="space-y-2 max-w-[720px]">
              {charity.source_documents.map((doc) => (
                <li key={doc.id}>
                  <button
                    type="button"
                    onClick={() => setOpenDoc(doc)}
                    className="text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink inline-flex items-center gap-2 text-left"
                  >
                    <HugeiconsIcon
                      icon={LinkSquare02Icon}
                      size={14}
                      aria-hidden="true"
                      className="text-ink-3"
                    />
                    {doc.label[lang] || doc.label.en}
                    {doc.file_format && (
                      <span className="font-mono text-caption text-ink-3 ml-1">
                        [{doc.file_format.toUpperCase()}]
                      </span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {/* === PRESS MENTIONS === */}
      {charity.news_mentions.length > 0 && (
        <section className="bg-surface-raised border-t border-rule">
          <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12 lg:py-16">
            <h2 className="font-serif text-h2 font-semibold text-ink mb-6">
              {t("charity.press")}
            </h2>
            <ul className="space-y-2 max-w-[720px]">
              {charity.news_mentions.map((mention) => (
                <li key={mention.url} className="text-body-sm text-ink-2">
                  <a
                    href={mention.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
                    lang={mention.language}
                  >
                    {mention.publisher}
                    <span className="text-ink-3"> — </span>
                    {mention.title}
                  </a>
                  <span className="text-ink-3 ml-2 font-mono text-caption">
                    {mention.published_date}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      <SourceDocumentDrawer
        document={openDoc}
        charityName={name}
        registrationId={charity.registration_id}
        onClose={() => setOpenDoc(null)}
      />

      <DonateConfirmModal
        open={donateOpen}
        onClose={() => setDonateOpen(false)}
        charityName={name}
        charitySlug={charity.slug}
        donationUrl={charity.donation_url}
        sourcePage="detail"
      />
    </div>
  )
}

/**
 * DetailHero — full-bleed 70vh photo with overlay text.
 * If no hero_photo_url, renders a tasteful cream/serif title block with no photo
 * (still readable, no broken-image state).
 */
function DetailHero({
  charity,
  name,
  tagline,
}: {
  charity: Charity
  name: string
  tagline: string
}) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const photoUrl = wikimediaThumb(charity.hero_photo_url, PHOTO_WIDTHS.detailHero)
  const credit = charity.hero_photo_credit ?? ""
  const license = charity.hero_photo_license ?? ""
  const photoCredit = credit
    ? license
      ? `${credit} / ${license}`
      : credit
    : ""
  const caption = charity.hero_photo_caption?.[lang] || charity.hero_photo_caption?.en || ""

  // === FALLBACK: no photo. Cream/serif title block. ===
  if (!photoUrl) {
    return (
      <header className="bg-paper border-b border-rule">
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12 lg:py-20">
          <Link
            to="/charities"
            className="inline-flex items-center gap-2 text-body-sm text-ink-3 hover:text-ink mb-8"
          >
            <HugeiconsIcon icon={ArrowLeft02Icon} size={16} />
            {t("charity.back")}
          </Link>
          <div className="flex items-start gap-6 flex-wrap">
            <CharityLogo
              logoUrl={charity.logo_url}
              slug={charity.slug}
              name={name}
              size="xl"
            />
            <div className="flex-1 min-w-0">
              <h1
                className="font-serif text-ink leading-tight"
                style={{
                  fontSize: "clamp(40px, 5vw, 56px)",
                  fontWeight: 700,
                  letterSpacing: "-0.02em",
                }}
              >
                {name}
              </h1>
              {tagline && (
                <p className="text-h4 font-normal text-ink-2 mt-3 max-w-[60ch]">
                  {tagline}
                </p>
              )}
              {charity.verification_status === "verified" && (
                <span className="mt-4 inline-flex items-center gap-1.5 bg-verified-soft text-verified text-body-sm font-medium rounded-full px-3 py-1">
                  <HugeiconsIcon icon={Tick02Icon} size={14} aria-hidden="true" />
                  {t("charity.verified")}
                </span>
              )}
            </div>
          </div>
        </div>
      </header>
    )
  }

  // === PHOTO HERO: full-bleed 70vh ===
  return (
    <header
      className="
        relative bg-ink overflow-hidden
        h-[55vh] md:h-[70vh]
        min-h-[360px] md:min-h-[480px]
      "
      aria-label={name}
    >
      <img
        src={photoUrl}
        alt=""
        loading="eager"
        decoding="sync"
        fetchPriority="high"
        className="absolute inset-0 h-full w-full object-cover object-center"
      />

      {/* Bottom-fade gradient overlay */}
      <div
        aria-hidden="true"
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(to top, rgba(10,12,11,0.85) 0%, rgba(10,12,11,0.4) 50%, transparent 80%)",
        }}
      />

      {/* Top-left: Back link (white) */}
      <Link
        to="/charities"
        className="
          absolute top-6 left-6 md:top-8 md:left-8 z-10
          inline-flex items-center gap-2 text-body-sm text-white/85 hover:text-white
          underline-offset-4 hover:underline decoration-white/40
        "
      >
        <HugeiconsIcon icon={ArrowLeft02Icon} size={16} aria-hidden="true" />
        {t("charity.back")}
      </Link>

      {/* Top-right: verified chip */}
      {charity.verification_status === "verified" && (
        <span
          className="
            absolute top-6 right-6 md:top-8 md:right-8 z-10
            inline-flex items-center gap-1.5
            bg-white/95 backdrop-blur-sm
            rounded-full px-4 py-1.5
            text-body-sm font-medium text-verified
            shadow-sm
          "
          aria-label={t("charity.verified")}
        >
          <HugeiconsIcon icon={Tick02Icon} size={14} aria-hidden="true" />
          {t("charity.verified")}
        </span>
      )}

      {/* Bottom-left: name + tagline */}
      <div
        className="
          absolute bottom-8 left-6 right-6 md:bottom-12 md:left-12 md:right-12 z-10
          max-w-(--container-default) mx-auto
        "
      >
        <h1
          className="font-serif text-white"
          style={{
            fontSize: "clamp(40px, 5vw, 72px)",
            lineHeight: 1.05,
            letterSpacing: "-0.02em",
            fontWeight: 700,
          }}
        >
          {name}
        </h1>
        {tagline && (
          <p
            className="mt-3 text-white/85 max-w-[60ch]"
            style={{ fontSize: "clamp(16px, 1.5vw, 20px)", lineHeight: 1.5 }}
          >
            {tagline}
          </p>
        )}
      </div>

      {/* Bottom-right: photo credit */}
      {photoCredit && (
        <div className="absolute bottom-3 right-4 md:bottom-4 md:right-6 z-10">
          <span className="text-[10px] leading-tight text-white/65 font-sans">
            {caption ? `${caption} — ` : ""}
            {t("detail.hero.photoCredit", { credit: photoCredit })}
          </span>
        </div>
      )}
    </header>
  )
}
