/**
 * LegitPage — "Is {charity} a legitimate charity?" SEO landing (v3.19).
 *
 * Targets the highest-intent long-tail query in MARKET_ANALYSIS.md §6.2
 * ("is [charity name] legitimate") that the detail page doesn't answer head-on.
 * The page leads with the literal question as the H1 and a one-line verdict,
 * then shows the regulator evidence and links straight to the source documents
 * — the whole "see the proof" wedge, framed as a direct answer.
 *
 * Data comes from the backend SEO endpoint (apps/seo), which already computes
 * the question, verdict, and evidence string per language. The Cloudflare
 * Worker injects the matching <title>/description + FAQPage JSON-LD at the edge
 * (worker/index.ts → handleLegitMeta) so crawlers and rich-result parsers see
 * the answer without running JS. This component is the human-facing render.
 *
 * URL: /charities/{slug}/legit
 */

import { ArrowRight01Icon, LinkSquare02Icon, Tick02Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"

import { DonateConfirmModal } from "@/components/charity/DonateConfirmModal"
import { api, ApiError } from "@/lib/api"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
import { usePreferences } from "@/store/preferences"

export function LegitPage() {
  const { slug = "" } = useParams<{ slug: string }>()
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const [donateOpen, setDonateOpen] = useState(false)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["seo-charity", slug, lang],
    queryFn: ({ signal }) => api.getSeoCharity(slug, lang, { signal }),
    enabled: Boolean(slug),
    retry: (failureCount, err) => {
      if (err instanceof ApiError && err.status === 404) return false
      return failureCount < 2
    },
  })

  const isNotFound = error instanceof ApiError && error.status === 404

  useDocumentTitle(data ? data.h1 : isNotFound ? t("catalog.notFound") : null)

  if (isLoading) {
    return (
      <div className="max-w-(--container-narrow) mx-auto px-6 lg:px-12 py-16">
        <div className="skeleton h-10 w-3/4 mb-6" />
        <div className="skeleton h-8 w-40 mb-8" />
        <div className="skeleton h-4 w-full max-w-[60ch] mb-2" />
        <div className="skeleton h-4 w-5/6 max-w-[60ch] mb-8" />
        <div className="skeleton h-12 w-64" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="max-w-(--container-narrow) mx-auto px-6 py-24 text-center">
        <h1 className="text-h2 font-semibold text-ink mb-3">
          {isNotFound ? t("catalog.notFound") : t("common.error")}
        </h1>
        <p className="text-body text-ink-2 mb-8 max-w-[60ch] mx-auto">
          {isNotFound ? t("catalog.notFoundBody") : t("common.errorBody")}
        </p>
        <Link
          to="/charities"
          className="inline-flex items-center gap-2 text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
        >
          {t("charity.back")}
        </Link>
      </div>
    )
  }

  const { charity } = data
  const name = charity.name[lang] || charity.name.en || charity.slug
  const isVerified = charity.verification_status === "verified"
  const evidence = data.evidence_summary[lang] || data.evidence_summary.en
  const donationHost = (() => {
    try {
      return new URL(charity.donation_url).hostname.replace(/^www\./, "")
    } catch {
      return charity.donation_url
    }
  })()

  return (
    <div className="bg-surface-raised">
      <div className="max-w-(--container-narrow) mx-auto px-6 lg:px-12 py-14 lg:py-20">
        {/* Question as H1 — matches the searched query verbatim. */}
        <h1
          className="font-serif text-ink leading-tight mb-6"
          style={{ fontSize: "clamp(30px, 4vw, 44px)", fontWeight: 700, letterSpacing: "-0.02em" }}
        >
          {data.h1}
        </h1>

        {/* One-line verdict — green chip when verified, muted otherwise. */}
        {isVerified ? (
          <span className="inline-flex items-center gap-1.5 bg-verified-soft text-verified text-body font-medium rounded-full px-4 py-1.5">
            <HugeiconsIcon icon={Tick02Icon} size={16} aria-hidden="true" />
            {data.answer}
          </span>
        ) : (
          <span className="inline-flex items-center bg-black/5 text-ink-2 text-body font-medium rounded-full px-4 py-1.5">
            {data.answer}
          </span>
        )}

        {/* Evidence — the regulator record behind the verdict. */}
        <p className="text-body text-ink-2 leading-relaxed max-w-[65ch] mt-8">{evidence}</p>

        {/* When we couldn't confirm a filing, say so plainly (v3.18 honesty rule). */}
        {!isVerified && (
          <p className="text-body-sm text-ink-3 leading-relaxed max-w-[65ch] mt-4">
            {t("charity.notVerifiedNote")}
          </p>
        )}

        {/* Source documents — the proof, linked directly. This is the wedge. */}
        {charity.source_documents.length > 0 && (
          <div className="mt-10 border-t border-rule pt-8">
            <h2 className="font-serif text-h3 font-semibold text-ink mb-4">
              {t("legit.evidenceHeading")}
            </h2>
            <ul className="space-y-2 max-w-[720px]">
              {charity.source_documents.map((doc) => (
                <li key={doc.id}>
                  <a
                    href={doc.url}
                    target="_blank"
                    rel="noopener noreferrer nofollow"
                    className="text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink inline-flex items-center gap-2"
                  >
                    <HugeiconsIcon
                      icon={LinkSquare02Icon}
                      size={14}
                      aria-hidden="true"
                      className="text-ink-3"
                    />
                    {doc.label[lang] || doc.label.en}
                    {doc.source_label && (
                      <span className="text-caption text-ink-3">— {doc.source_label}</span>
                    )}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Actions — full profile (internal link, keeps crawl equity on-site) and
            the direct donate CTA (logged as a seo_landing conversion). */}
        <div className="mt-10 flex flex-col sm:flex-row gap-3">
          <Link
            to={`/charities/${charity.slug}`}
            className="inline-flex items-center justify-center gap-2 border border-rule rounded-md px-5 py-3 text-body font-medium text-ink hover:border-ink"
          >
            {t("legit.viewProfile")}
            <HugeiconsIcon icon={ArrowRight01Icon} size={16} aria-hidden="true" />
          </Link>
          {charity.donation_url && (
            <button
              type="button"
              onClick={() => setDonateOpen(true)}
              className="inline-flex items-center justify-center gap-2 bg-verified text-verified-on rounded-md px-5 py-3 text-body font-medium hover:opacity-90"
            >
              {t("detail.donate.cta", { hostname: donationHost })}
              <HugeiconsIcon icon={ArrowRight01Icon} size={16} aria-hidden="true" />
            </button>
          )}
        </div>
        <p className="text-caption text-ink-3 mt-3">{t("detail.donate.microcopy")}</p>
      </div>

      {charity.donation_url && (
        <DonateConfirmModal
          open={donateOpen}
          onClose={() => setDonateOpen(false)}
          charityName={name}
          charitySlug={charity.slug}
          donationUrl={charity.donation_url}
          sourcePage="seo_landing"
        />
      )}
    </div>
  )
}
