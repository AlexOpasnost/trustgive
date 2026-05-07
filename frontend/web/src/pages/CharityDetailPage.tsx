/**
 * CharityDetailPage — restructured per DESIGN.md v2.0 §B.
 *
 * Above-the-fold target (1024×720 desktop / 390×844 iPhone):
 *   1. Back link
 *   2. Hero: logo (96px) + name + tagline + EIN/country/founded + verified chip
 *   3. Description block — RIGHT BELOW hero, NOT below money breakdown
 *   4. Donate primary CTA + 0%-commission microcopy
 *
 * Below the fold:
 *   5. Stale-data warning (if applicable, demoted from above)
 *   6. Methodology
 *   7. Money breakdown (with §F.3 empty-state when only total_revenue is populated)
 *   8. Source documents drawer (existing)
 *   9. Press mentions
 */

import { ArrowLeft02Icon, ArrowRight01Icon, LinkSquare02Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"

import { CharityLogo } from "@/components/charity/CharityLogo"
import { DonateConfirmModal } from "@/components/charity/DonateConfirmModal"
import { MoneyBreakdown } from "@/components/charity/MoneyBreakdown"
import { SourceDocumentDrawer } from "@/components/charity/SourceDocumentDrawer"
import { VerificationBadge } from "@/components/charity/VerificationBadge"
import { Button } from "@/components/ui/Button"
import { api } from "@/lib/api"
import { usePreferences } from "@/store/preferences"
import type { SourceDocument } from "@/types/api"

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
      <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12">
        <div className="skeleton h-5 w-32 mb-8" />
        <div className="flex items-start gap-6 mb-8">
          <div className="skeleton w-24 h-24 rounded-md" />
          <div className="flex-1 space-y-3">
            <div className="skeleton h-10 w-2/3" />
            <div className="skeleton h-5 w-1/2" />
            <div className="skeleton h-4 w-1/3" />
          </div>
        </div>
        <div className="skeleton h-40 w-full max-w-[720px] mb-6" />
        <div className="skeleton h-12 w-64 mb-12" />
        <div className="skeleton h-64 w-full" />
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
    <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12">
      {/* Back link */}
      <Link
        to="/charities"
        className="inline-flex items-center gap-2 text-body-sm text-ink-3 hover:text-ink mb-8"
      >
        <HugeiconsIcon icon={ArrowLeft02Icon} size={16} />
        {t("charity.back")}
      </Link>

      {/* === HERO (above the fold) === */}
      <header className="mb-6 flex flex-wrap items-start justify-between gap-6">
        <div className="flex items-start gap-5 flex-1 min-w-0">
          <CharityLogo
            logoUrl={charity.logo_url}
            slug={charity.slug}
            name={name}
            size="xl"
          />
          <div className="flex-1 min-w-0">
            <h1 className="text-h1 font-semibold text-ink leading-tight">{name}</h1>
            {tagline && (
              <p className="text-h4 font-normal text-ink-2 mt-2 max-w-[60ch]">{tagline}</p>
            )}
            <p className="text-body-sm text-ink-3 mt-3 font-mono">
              EIN/Reg {charity.registration_id} · {charity.country}
              {charity.founded_year && ` · Founded ${charity.founded_year}`}
            </p>
          </div>
        </div>
        <VerificationBadge status={charity.verification_status} />
      </header>

      {/* === DESCRIPTION (above the fold, immediately below hero) === */}
      {description && (
        <section className="mb-6 max-w-[720px]">
          <h2 className="sr-only">{t("detail.about")}</h2>
          <p className="text-body text-ink-2 leading-relaxed">{description}</p>
        </section>
      )}

      {/* === DONATE CTA (above the fold) === */}
      {charity.donation_url ? (
        <section className="mb-12 max-w-[480px]">
          <Button
            variant="primary"
            size="lg"
            className="w-full"
            onClick={() => setDonateOpen(true)}
          >
            {t("detail.donate.cta", { hostname: donationHost })}
            <HugeiconsIcon icon={ArrowRight01Icon} size={16} aria-hidden="true" />
          </Button>
          <p className="text-body-sm text-ink-2 mt-3 text-center">
            {t("detail.donate.microcopy")}
          </p>
        </section>
      ) : null}

      {/* === STALE-DATA WARNING (demoted, below the fold) === */}
      {charity.is_stale && charity.last_filed_date && (
        <div
          className="bg-warning-soft border-l-4 border-warning px-4 py-3 mb-10 rounded-md"
          role="status"
        >
          <p className="text-body-sm text-warning">
            {t("charity.staleWarning", { date: charity.last_filed_date })}
          </p>
        </div>
      )}

      {/* === METHODOLOGY === */}
      {methodology && (
        <section className="max-w-[720px] mb-10">
          <h2 className="text-h3 font-semibold text-ink mb-3">{t("detail.methodology")}</h2>
          <p className="text-body text-ink-2 leading-relaxed">{methodology}</p>
        </section>
      )}

      {/* === MONEY BREAKDOWN (demoted, with §F.3 empty-state) === */}
      <div className="mb-10 max-w-[720px]">
        <MoneyBreakdown
          data={charity.money_breakdown}
          totalRevenueUsd={charity.total_revenue_usd}
          fallbackYear={charity.last_filed_date ? Number(charity.last_filed_date.slice(0, 4)) : null}
        />
      </div>

      {/* === SOURCE DOCUMENTS === */}
      {charity.source_documents.length > 0 && (
        <section className="max-w-[720px] mb-10">
          <h2 className="text-h3 font-semibold text-ink mb-4">
            {t("charity.sourceDocuments")}
          </h2>
          <ul className="space-y-2">
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
        </section>
      )}

      {/* === PRESS MENTIONS === */}
      {charity.news_mentions.length > 0 && (
        <section className="max-w-[720px] mb-10">
          <h2 className="text-h3 font-semibold text-ink mb-4">{t("charity.press")}</h2>
          <ul className="space-y-2">
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
