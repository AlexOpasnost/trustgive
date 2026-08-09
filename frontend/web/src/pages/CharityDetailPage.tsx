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

import { CharityHubLinks } from "@/components/catalog/CharityHubLinks"
import { CharityLogo } from "@/components/charity/CharityLogo"
import { VerificationLine } from "@/components/charity/VerificationLine"
import { DonateConfirmModal } from "@/components/charity/DonateConfirmModal"
import { MoneyBreakdown } from "@/components/charity/MoneyBreakdown"
import { SourceDocumentDrawer } from "@/components/charity/SourceDocumentDrawer"
import { Button } from "@/components/ui/Button"
import { api, ApiError } from "@/lib/api"
import { PHOTO_WIDTHS, SRCSET_WIDTHS, buildSrcSet, wikimediaThumb } from "@/lib/image"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
import { usePreferences } from "@/store/preferences"
import type { Charity, SourceDocument } from "@/types/api"

export function CharityDetailPage() {
  const { slug = "" } = useParams<{ slug: string }>()
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const [openDoc, setOpenDoc] = useState<SourceDocument | null>(null)
  const [donateOpen, setDonateOpen] = useState(false)

  const { data: charity, isLoading, isError, error } = useQuery({
    queryKey: ["charity", slug],
    queryFn: ({ signal }) => api.getCharity(slug, { signal }),
    enabled: Boolean(slug),
    // Don't auto-retry 404 — the slug is genuinely missing.
    retry: (failureCount, err) => {
      if (err instanceof ApiError && err.status === 404) return false
      return failureCount < 2
    },
  })

  const isNotFound = error instanceof ApiError && error.status === 404

  // Title: charity name once loaded, "Charity not found" on a 404, otherwise
  // null (leave the default brand title untouched while loading).
  useDocumentTitle(
    charity
      ? charity.name[lang] || charity.name.en || charity.slug
      : isNotFound
        ? t("catalog.notFound")
        : null,
  )

  if (isLoading) {
    return (
      <div>
        {/* Hero skeleton — same height as real hero to avoid CLS */}
        <div className="relative bg-stone-200 h-[55vh] md:h-[70vh] min-h-[360px]">
          <div className="absolute inset-0 skeleton" />
        </div>
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 band-tight">
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
    if (isNotFound) {
      return (
        <div className="max-w-(--container-narrow) mx-auto px-6 band-state text-center">
          <h1 className="text-h2 font-semibold text-ink mb-3">
            {t("catalog.notFound")}
          </h1>
          <p className="text-body text-ink-2 mb-8 max-w-[60ch] mx-auto">
            {t("catalog.notFoundBody")}
          </p>
          <Link
            to="/charities"
            className="inline-flex items-center gap-2 text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            <HugeiconsIcon icon={ArrowLeft02Icon} size={14} aria-hidden="true" />
            {t("charity.back")}
          </Link>
        </div>
      )
    }
    return (
      <div className="max-w-(--container-narrow) mx-auto px-6 band-state text-center">
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
      {/* === PHOTO BAND === */}
      <DetailHero charity={charity} name={name} />

      {/* === IDENTITY + EVIDENCE (first thing under the photo band) ===
          v3.21: this used to sit below a photo filling 70% of the viewport, and
          carried the name a second time next to a bare "Verified" pill, with the
          filing dates exiled to a grey column on the right. The evidence is the
          product, so it now opens the page: name, then the verification line,
          then the identifiers. The name appears once. */}
      <section className="bg-surface-raised border-b border-rule">
        {/* py-8 rather than one of the rhythm bands on purpose: this is the
            page's identity strip, not a section of it, and it has to sit close
            under the header the way a masthead does. */}
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-8">
          <div className="flex items-start gap-4 md:gap-6">
            <CharityLogo
              logoUrl={charity.logo_url}
              slug={charity.slug}
              name={name}
              size="lg"
            />
            <div className="min-w-0 flex-1">
              <h1 className="font-serif text-section font-bold text-ink">{name}</h1>
              {tagline && (
                <p className="text-body text-ink-2 mt-2 max-w-[60ch]">{tagline}</p>
              )}

              {/* The line the whole page exists for. */}
              <VerificationLine charity={charity} onOpenFiling={setOpenDoc} />

              {/* The stored filing date is the fiscal-period end reported on the
                  return (ProPublica `tax_prd`), not the day it was submitted —
                  the verification line labels it for exactly that. */}
              <p className="text-body-sm text-ink-3 mt-4">
                {/* Dropped entirely when unknown rather than rendered empty.
                    `registration_id` is nullable, and a row with none is one
                    whose stored number turned out to belong to a different
                    organisation — "EIN/Reg" followed by nothing would read as a
                    display bug rather than as an absent fact. */}
                {charity.registration_id && (
                  <>
                    <span className="font-mono">EIN/Reg {charity.registration_id}</span>
                    <span className="mx-2">·</span>
                  </>
                )}
                <span>{charity.country}</span>
                {charity.founded_year && (
                  <>
                    <span className="mx-2">·</span>
                    <span>{t("charity.founded", { year: charity.founded_year })}</span>
                  </>
                )}
              </p>

              <Link
                to={`/charities/${charity.slug}/legit`}
                className="inline-block mt-2 text-body-sm text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
              >
                {t("legit.fromProfileLink", { name })}
              </Link>
            </div>
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
          <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 band-tight">
            <h2 className="font-serif text-h2 font-semibold text-ink mb-4">
              {t("detail.methodology")}
            </h2>
            <p className="font-serif text-prose text-ink-2 max-w-[65ch] italic">{methodology}</p>
          </div>
        </section>
      )}

      {/* === WHERE THE MONEY GOES === */}
      {/* Only render when there's a verified financial figure to show. When a
          charity's source filing couldn't be verified (v3.18 audit), its
          financials are nulled, and MoneyBreakdown would render nothing — so we
          drop the whole section rather than leave a dangling header. */}
      {(charity.money_breakdown || charity.total_revenue_usd != null) && (
        <section className="bg-surface-raised">
          <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 band-tight">
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
      )}

      {/* === SOURCE DOCUMENTS === */}
      {charity.source_documents.length > 0 && (
        <section className="bg-surface-raised border-t border-rule">
          <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 band-tight">
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

      {/* No source document → say so honestly, rather than silently omit the
          section. Every charity must communicate its trust state (v3.18). */}
      {charity.source_documents.length === 0 && (
        <section className="bg-surface-raised border-t border-rule">
          <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 band-tight">
            <h2 className="font-serif text-h2 font-semibold text-ink mb-4">
              {t("charity.sourceDocuments")}
            </h2>
            <p className="text-body text-ink-2 max-w-[65ch]">
              {t("charity.notVerifiedNote")}
            </p>
          </div>
        </section>
      )}

      {/* === WHAT WE DIDN'T CHECK ===
          Permanent, on every profile, whatever the charity's status (STRATEGY
          §5.7). A green "Verified" badge reads as "recommended" unless the page
          says otherwise in words, and this catalogue makes a far narrower claim:
          the organisation is registered and has filed. Nothing here is an
          opinion about how well it spends the money, because nothing here
          measures that. */}
      <section className="bg-paper border-t border-rule">
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 band-tight">
          <h2 className="font-serif text-h2 font-semibold text-ink mb-4">
            {t("charity.notChecked.title")}
          </h2>
          <p className="text-body text-ink-2 max-w-[65ch] leading-relaxed">
            {t("charity.notChecked.body")}
          </p>
          <Link
            to="/methodology"
            className="inline-flex items-center gap-2 mt-5 text-body-sm text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("charity.notChecked.cta")}
            <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
          </Link>
        </div>
      </section>

      {/* === PRESS MENTIONS === */}
      {charity.news_mentions.length > 0 && (
        <section className="bg-surface-raised border-t border-rule">
          <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 band-tight">
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

      {/* === RELATED SECTIONS (country / registry / cause hubs) === */}
      <CharityHubLinks charity={charity} />

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
 * DetailHero — a photo band, not a cover.
 *
 * v3.21 (STRATEGY.md §5): the photo used to occupy 55–70% of the viewport with
 * the name and tagline burned into it, which pushed the evidence — the reason
 * anyone is on this page — below the fold, and printed the name a second time
 * three centimetres above where the identity strip printed it again. It is now
 * a ~30vh band carrying only navigation, trust state and the credit the licence
 * requires. Name, tagline and the verification line live in the section below,
 * where they are the first thing read.
 *
 * With no photo the band collapses to a slim paper strip rather than a large
 * empty title block — same structure either way, so the page below never has to
 * care which variant rendered.
 */
function DetailHero({ charity, name }: { charity: Charity; name: string }) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const photoUrl = wikimediaThumb(charity.hero_photo_url, PHOTO_WIDTHS.detailHero)
  const photoSrcSet = buildSrcSet(charity.hero_photo_url, SRCSET_WIDTHS.detailHero)
  const credit = charity.hero_photo_credit ?? ""
  const license = charity.hero_photo_license ?? ""
  const photoCredit = credit ? (license ? `${credit} / ${license}` : credit) : ""
  const caption = charity.hero_photo_caption?.[lang] || charity.hero_photo_caption?.en || ""

  const isVerified = charity.verification_status === "verified"

  // === FALLBACK: no photo. Slim paper strip with the back link. ===
  if (!photoUrl) {
    return (
      <header className="bg-paper border-b border-rule">
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-5">
          <Link
            to="/charities"
            className="inline-flex items-center gap-2 text-body-sm text-ink-3 hover:text-ink"
          >
            <HugeiconsIcon icon={ArrowLeft02Icon} size={16} aria-hidden="true" />
            {t("charity.back")}
          </Link>
        </div>
      </header>
    )
  }

  // === PHOTO BAND ===
  return (
    <header
      className="
        relative bg-ink overflow-hidden
        h-[26vh] md:h-[30vh]
        min-h-[180px] md:min-h-[240px]
      "
      aria-label={name}
    >
      <img
        src={photoUrl}
        {...(photoSrcSet ? { srcSet: photoSrcSet } : {})}
        sizes="100vw"
        alt=""
        loading="eager"
        decoding="sync"
        fetchPriority="high"
        crossOrigin="anonymous"
        className="absolute inset-0 h-full w-full object-cover object-center"
      />

      {/* Gradient kept top and bottom: the band is short, so the back link at the
          top needs its own contrast floor rather than relying on the photo. */}
      <div
        aria-hidden="true"
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(to bottom, rgba(10,12,11,0.55) 0%, rgba(10,12,11,0.15) 40%, rgba(10,12,11,0.55) 100%)",
        }}
      />

      <Link
        to="/charities"
        className="
          absolute top-4 left-6 md:top-5 md:left-12 z-10
          inline-flex items-center gap-2 text-body-sm text-white/90 hover:text-white
          underline-offset-4 hover:underline decoration-white/40
        "
      >
        <HugeiconsIcon icon={ArrowLeft02Icon} size={16} aria-hidden="true" />
        {t("charity.back")}
      </Link>

      {/* Trust state stays on the band so it is visible before any scrolling,
          even though the full verification line repeats it below (v3.18: a
          charity's trust state is never blank). */}
      <span
        className={`
          absolute top-4 right-6 md:top-5 md:right-12 z-10
          inline-flex items-center gap-1.5
          backdrop-blur-sm rounded-full px-4 py-1.5
          text-body-sm font-medium shadow-sm
          ${isVerified ? "bg-white/95 text-verified" : "bg-white/80 text-ink-3"}
        `}
        aria-label={isVerified ? t("charity.verified") : t("charity.notVerified")}
      >
        {isVerified && <HugeiconsIcon icon={Tick02Icon} size={14} aria-hidden="true" />}
        {isVerified ? t("charity.verified") : t("charity.notVerified")}
      </span>

      {/* Photo credit — a licence requirement, so it stays at every width. The
          descriptive caption is desktop-only; at 320px it wraps into the band. */}
      {photoCredit && (
        <div className="absolute bottom-2 left-6 right-6 md:left-auto md:bottom-3 md:right-12 z-10 text-right">
          <span className="text-[10px] leading-tight text-white/70 font-sans">
            {caption && <span className="hidden md:inline">{caption} — </span>}
            {t("detail.hero.photoCredit", { credit: photoCredit })}
          </span>
        </div>
      )}
    </header>
  )
}
