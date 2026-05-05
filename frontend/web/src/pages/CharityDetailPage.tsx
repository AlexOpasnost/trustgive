import { HugeiconsIcon } from "@hugeicons/react"
import { ArrowLeft02Icon, ArrowUpRight01Icon } from "@hugeicons/core-free-icons"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"

import { DonateConfirmModal } from "@/components/charity/DonateConfirmModal"
import { MoneyBreakdown } from "@/components/charity/MoneyBreakdown"
import { SourceDocumentDrawer } from "@/components/charity/SourceDocumentDrawer"
import { VerificationBadge } from "@/components/charity/VerificationBadge"
import { api } from "@/lib/api"
import type { SourceDocument } from "@/types/api"
import { usePreferences } from "@/store/preferences"

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
        <div className="skeleton h-8 w-2/3 mb-4" />
        <div className="skeleton h-5 w-1/2 mb-12" />
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 skeleton h-96" />
          <div className="space-y-3">
            <div className="skeleton h-12 w-full" />
            <div className="skeleton h-32 w-full" />
          </div>
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
    <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-12">
      <Link to="/charities" className="inline-flex items-center gap-2 text-body-sm text-ink-3 hover:text-ink mb-8">
        <HugeiconsIcon icon={ArrowLeft02Icon} size={16} />
        {t("charity.back")}
      </Link>

      <header className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-4">
          {charity.logo_url ? (
            <img src={charity.logo_url} alt="" className="w-20 h-20 rounded-md object-cover" />
          ) : (
            <div className="w-20 h-20 rounded-md bg-info-soft text-info flex items-center justify-center text-h2 font-semibold">
              {name.slice(0, 1).toUpperCase()}
            </div>
          )}
          <div>
            <h1 className="text-h1 font-semibold text-ink">{name}</h1>
            {tagline && <p className="text-body text-ink-2 mt-1">{tagline}</p>}
            <p className="text-body-sm text-ink-3 mt-1 font-mono">
              EIN/Reg {charity.registration_id} · {charity.country}
              {charity.founded_year && ` · Founded ${charity.founded_year}`}
            </p>
          </div>
        </div>
        <VerificationBadge status={charity.verification_status} />
      </header>

      {charity.is_stale && charity.last_filed_date && (
        <div className="bg-warning-soft border-l-4 border-warning px-4 py-3 mb-8 rounded-md">
          <p className="text-body-sm text-warning">⚠ {t("charity.staleWarning", { date: charity.last_filed_date })}</p>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6 mb-12">
        <div className="lg:col-span-2 space-y-6">
          {charity.money_breakdown && <MoneyBreakdown data={charity.money_breakdown} />}
        </div>

        <aside className="lg:sticky lg:top-20 self-start space-y-6">
          {charity.donation_url && (
            <div className="bg-surface border border-rule rounded-md p-5">
              <button
                type="button"
                onClick={() => setDonateOpen(true)}
                className="w-full bg-verified text-verified-on rounded-md px-4 py-3 font-medium inline-flex items-center justify-center gap-2 hover:opacity-90"
              >
                {t("charity.donateOn", { site: donationHost })}
                <HugeiconsIcon icon={ArrowUpRight01Icon} size={16} />
              </button>
              <p className="text-body-sm text-ink-2 mt-3">{t("charity.noFee")}</p>
            </div>
          )}

          <div className="bg-surface border border-rule rounded-md p-5">
            <h2 className="text-h4 font-semibold text-ink mb-3">{t("charity.sourceDocuments")}</h2>
            {charity.source_documents.length > 0 ? (
              <ul className="space-y-2">
                {charity.source_documents.map((doc) => (
                  <li key={doc.id}>
                    <button
                      type="button"
                      onClick={() => setOpenDoc(doc)}
                      className="text-body-sm text-verified hover:underline text-left inline-flex items-center gap-1"
                    >
                      → {doc.label[lang] || doc.label.en}
                      {doc.file_format && (
                        <span className="font-mono text-caption text-ink-3 ml-1">
                          [{doc.file_format.toUpperCase()}]
                        </span>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-body-sm text-ink-3">No source documents on record yet.</p>
            )}
          </div>
        </aside>
      </div>

      {description && (
        <section className="max-w-(--container-narrow) mb-10">
          <h2 className="text-h3 font-semibold text-ink mb-3">{t("charity.description")}</h2>
          <p className="text-body text-ink-2 leading-relaxed">{description}</p>
        </section>
      )}

      {charity.news_mentions.length > 0 && (
        <section className="max-w-(--container-narrow) mb-10">
          <h2 className="text-h3 font-semibold text-ink mb-3">{t("charity.press")}</h2>
          <ul className="space-y-2">
            {charity.news_mentions.map((mention) => (
              <li key={mention.url} className="text-body-sm text-ink-2">
                <a
                  href={mention.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-verified hover:underline"
                  lang={mention.language}
                >
                  {mention.publisher}
                  <span className="text-ink-3"> — </span>
                  {mention.title}
                </a>
                <span className="text-ink-3 ml-2 font-mono text-caption">{mention.published_date}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {methodology && (
        <section className="max-w-(--container-narrow) mb-10">
          <h2 className="text-h3 font-semibold text-ink mb-3">{t("charity.methodology")}</h2>
          <p className="text-body text-ink-2 leading-relaxed">{methodology}</p>
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
