/**
 * CharityDetailPage — DESIGN_v4.md §6.3 (editorial detail page).
 *
 * v4 inverts v3's photo-first layout. The name and dek live above the
 * fold in type on paper; the hero photo drops below the rule, becoming an
 * illustration. The source-documents module is upgraded from a click-to-
 * open drawer into a permanent right-rail block — typeset like a journal-
 * of-record masthead. The rail is the climax of the page.
 *
 * Page order:
 *   1. Breadcrumb (← All charities)
 *   2. Eyebrow caption (US · founded 2001)
 *   3. Display-lg name
 *   4. Italic dek (tagline)
 *   5. Hairline rule
 *   6. Two-col grid:
 *      - Left col (8/12): hero photo (3:2 aspect) + description body with
 *        a 2-line drop cap on the first paragraph
 *      - Right col (4/12): SOURCE DOCUMENTS rail (paper-2 bg, hairline-
 *        soft between entries, EIN at bottom)
 *   7. Stale-data warning (kept, repositioned)
 *   8. How to give (h2 + body + bordered CTA — no rounded, no green)
 *   9. Where the money goes (MoneyBreakdown)
 *   10. Methodology (italic serif essay)
 *   11. Press mentions (list)
 *
 * Drawer for full-source-doc preview is kept — click any rail row to open.
 */

import { ArrowLeft02Icon, ArrowRight01Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, useParams } from "react-router-dom"

import { DonateConfirmModal } from "@/components/charity/DonateConfirmModal"
import { MoneyBreakdown } from "@/components/charity/MoneyBreakdown"
import { SourceDocumentDrawer } from "@/components/charity/SourceDocumentDrawer"
import { countryLabel } from "@/lib/countryLabels"
import { api, ApiError } from "@/lib/api"
import { PHOTO_WIDTHS, SRCSET_WIDTHS, buildSrcSet, wikimediaThumb } from "@/lib/image"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
import { usePreferences } from "@/store/preferences"
import type { SourceDocument } from "@/types/api"

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
    retry: (failureCount, err) => {
      if (err instanceof ApiError && err.status === 404) return false
      return failureCount < 2
    },
  })

  const isNotFound = error instanceof ApiError && error.status === 404

  useDocumentTitle(
    charity
      ? charity.name[lang] || charity.name.en || charity.slug
      : isNotFound
        ? t("catalog.notFound")
        : null,
  )

  if (isLoading) {
    return (
      <main
        style={{ background: "var(--color-paper-v4)" }}
        className="px-6 lg:px-12 max-w-[1280px] mx-auto pt-16 pb-24"
      >
        <div className="skeleton h-4 w-32 mb-12" />
        <div className="skeleton h-3 w-48 mb-6" />
        <div className="skeleton h-14 w-3/4 mb-4" />
        <div className="skeleton h-14 w-2/3 mb-8" />
        <div className="skeleton h-6 w-full max-w-[60ch] mb-10" />
        <div className="grid lg:grid-cols-12 gap-10">
          <div className="lg:col-span-8">
            <div className="aspect-[3/2] skeleton mb-8" />
            <div className="skeleton h-4 w-full mb-2" />
            <div className="skeleton h-4 w-full mb-2" />
            <div className="skeleton h-4 w-4/5" />
          </div>
          <div className="lg:col-span-4">
            <div className="skeleton h-48 w-full" />
          </div>
        </div>
      </main>
    )
  }

  if (isError || !charity) {
    if (isNotFound) {
      return (
        <main
          style={{ background: "var(--color-paper-v4)", color: "var(--color-ink-v4)" }}
          className="px-6 lg:px-12 max-w-[800px] mx-auto py-24 lg:py-32 text-center"
        >
          <h1
            className="font-serif mb-6"
            style={{
              fontSize: "clamp(36px, 5vw, 56px)",
              lineHeight: 1.1,
              fontWeight: 400,
              letterSpacing: "-0.015em",
            }}
          >
            {t("catalog.notFound")}
          </h1>
          <p
            className="font-serif italic mb-10 max-w-[55ch] mx-auto"
            style={{
              fontSize: "var(--text-body-lg)",
              lineHeight: "var(--text-body-lg--line-height)",
              color: "var(--color-ink-2-v4)",
            }}
          >
            {t("catalog.notFoundBody")}
          </p>
          <Link
            to="/charities"
            className="font-sans inline-flex items-center gap-2 group"
            style={{
              fontSize: "var(--text-ui-md)",
              color: "var(--color-link)",
              fontWeight: 500,
            }}
          >
            <HugeiconsIcon icon={ArrowLeft02Icon} size={14} aria-hidden="true" />
            <span className="underline decoration-1 underline-offset-4 group-hover:no-underline">
              {t("detail.v4.backToArchive")}
            </span>
          </Link>
        </main>
      )
    }
    return (
      <main
        style={{ background: "var(--color-paper-v4)" }}
        className="px-6 max-w-[640px] mx-auto py-24 text-center"
      >
        <p
          className="font-serif italic"
          style={{
            fontSize: "var(--text-body-lg)",
            color: "var(--color-ink-2-v4)",
          }}
        >
          {t("common.errorBody")}
        </p>
      </main>
    )
  }

  const name = charity.name[lang] || charity.name.en || charity.slug
  const tagline = charity.tagline[lang] || charity.tagline.en || ""
  const description = charity.description[lang] || charity.description.en || ""
  const methodology = charity.methodology_note[lang] || charity.methodology_note.en || ""
  const country = countryLabel(charity.country, lang)
  const donationHost = (() => {
    try {
      return new URL(charity.donation_url).hostname.replace(/^www\./, "")
    } catch {
      return charity.donation_url
    }
  })()

  const heroPhoto = wikimediaThumb(charity.hero_photo_url, PHOTO_WIDTHS.detailHero)
  const heroSrcSet = buildSrcSet(charity.hero_photo_url, SRCSET_WIDTHS.detailHero)
  const heroCaption = charity.hero_photo_caption?.[lang] || charity.hero_photo_caption?.en || ""
  const heroCredit = charity.hero_photo_credit ?? ""
  const heroLicense = charity.hero_photo_license ?? ""

  // Split description into paragraphs. First paragraph gets a drop cap.
  const paragraphs = description.split(/\n\s*\n/).filter((p) => p.trim())

  const regPrefix =
    charity.country === "US" ? "EIN" : charity.country === "GB" ? "CC" : "Reg"

  // Group documents by year for chronological reading order.
  const sortedDocs = [...charity.source_documents].sort((a, b) => {
    const ya = a.filed_date ?? ""
    const yb = b.filed_date ?? ""
    return yb.localeCompare(ya)
  })

  return (
    <main
      style={{
        background: "var(--color-paper-v4)",
        color: "var(--color-ink-v4)",
      }}
    >
      <div className="px-6 lg:px-12 max-w-[1280px] mx-auto pt-10 lg:pt-14 pb-24">
        {/* ============= BREADCRUMB ============= */}
        <Link
          to="/charities"
          className="font-sans inline-flex items-center gap-2 mb-10 lg:mb-16 group"
          style={{
            fontSize: "var(--text-ui-sm)",
            color: "var(--color-ink-3-v4)",
            fontWeight: 500,
          }}
        >
          <HugeiconsIcon icon={ArrowLeft02Icon} size={12} aria-hidden="true" />
          <span className="group-hover:underline decoration-1 underline-offset-4">
            {t("detail.v4.backToArchive")}
          </span>
        </Link>

        {/* ============= EYEBROW ============= */}
        <p
          className="font-sans uppercase mb-6"
          style={{
            fontSize: "var(--text-ui-sm)",
            lineHeight: "var(--text-ui-sm--line-height)",
            letterSpacing: "0.16em",
            color: "var(--color-ink-3-v4)",
            fontWeight: 500,
          }}
        >
          {country}
          {charity.founded_year && (
            <>
              <span className="mx-2">·</span>
              <span>Founded {charity.founded_year}</span>
            </>
          )}
        </p>

        {/* ============= NAME ============= */}
        <h1
          className="font-serif mb-6"
          style={{
            fontSize: "clamp(40px, 6vw, 64px)",
            lineHeight: 1.05,
            fontWeight: 400,
            letterSpacing: "-0.015em",
            color: "var(--color-ink-v4)",
            maxWidth: "20ch",
          }}
        >
          {name}
        </h1>

        {/* ============= DEK ============= */}
        {tagline && (
          <p
            className="font-serif italic max-w-[55ch] mb-10 lg:mb-14"
            style={{
              fontSize: "var(--text-dek)",
              lineHeight: "var(--text-dek--line-height)",
              color: "var(--color-ink-2-v4)",
            }}
          >
            {tagline}
          </p>
        )}

        {/* ============= STALE-DATA WARNING ============= */}
        {charity.is_stale && charity.last_filed_date && (
          <div
            role="status"
            className="mb-10 px-4 py-3 max-w-[720px]"
            style={{
              background: "var(--color-paper-2-v4)",
              borderLeft: "2px solid var(--color-link)",
              fontSize: "var(--text-body-sm-v4)",
              lineHeight: "var(--text-body-sm-v4--line-height)",
              color: "var(--color-ink-2-v4)",
            }}
          >
            {t("charity.staleWarning", { date: charity.last_filed_date })}
          </div>
        )}

        <div style={{ borderTop: "1px solid var(--color-rule-v4)" }} className="mb-10 lg:mb-14" />

        {/* ============= TWO-COL: HERO + BODY | SOURCE DOCS RAIL ============= */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14">
          <div className="lg:col-span-8">
            {/* Hero photo — demoted to illustration, 3:2 */}
            {heroPhoto && (
              <figure className="mb-10 lg:mb-12">
                <div
                  className="relative aspect-[3/2] overflow-hidden"
                  style={{ background: "var(--color-paper-2-v4)" }}
                >
                  <img
                    src={heroPhoto}
                    {...(heroSrcSet ? { srcSet: heroSrcSet } : {})}
                    sizes="(min-width: 1024px) 66vw, 92vw"
                    alt=""
                    loading="eager"
                    decoding="async"
                    crossOrigin="anonymous"
                    className="absolute inset-0 h-full w-full object-cover object-center"
                  />
                </div>
                {(heroCaption || heroCredit) && (
                  <figcaption
                    className="font-sans mt-3"
                    style={{
                      fontSize: "var(--text-ui-sm)",
                      lineHeight: "var(--text-ui-sm--line-height)",
                      color: "var(--color-ink-3-v4)",
                    }}
                  >
                    {heroCaption}
                    {heroCaption && heroCredit && <span className="mx-2">·</span>}
                    {heroCredit && (
                      <span>
                        {t("detail.hero.photoCredit", { credit: heroCredit })}
                        {heroLicense && (
                          <>
                            <span className="mx-1">/</span>
                            <span>{heroLicense}</span>
                          </>
                        )}
                      </span>
                    )}
                  </figcaption>
                )}
              </figure>
            )}

            {/* Body — Source Serif 20px reading column, drop cap on first paragraph */}
            <article className="max-w-[640px]">
              {paragraphs.map((para, idx) => (
                <p
                  key={idx}
                  className={`font-serif mb-6 ${idx === 0 ? "v4-drop-cap" : ""}`}
                  style={{
                    fontSize: "var(--text-body-lg)",
                    lineHeight: "var(--text-body-lg--line-height)",
                    color: "var(--color-ink-v4)",
                  }}
                >
                  {para}
                </p>
              ))}
            </article>
          </div>

          {/* ============= SOURCE DOCUMENTS RAIL ============= */}
          <aside className="lg:col-span-4">
            <div
              className="px-6 py-7"
              style={{ background: "var(--color-paper-2-v4)" }}
            >
              <p
                className="font-sans uppercase mb-6"
                style={{
                  fontSize: "var(--text-ui-sm)",
                  letterSpacing: "0.16em",
                  color: "var(--color-ink-3-v4)",
                  fontWeight: 500,
                }}
              >
                {t("detail.v4.sourceDocsTitle")}
              </p>

              {sortedDocs.length > 0 ? (
                <ul>
                  {sortedDocs.map((doc, i) => {
                    const year = doc.filed_date ? doc.filed_date.slice(0, 4) : ""
                    return (
                      <li
                        key={doc.id}
                        style={
                          i < sortedDocs.length - 1
                            ? { borderBottom: "1px solid var(--color-rule-soft-v4)" }
                            : undefined
                        }
                        className="py-4 first:pt-0 last:pb-0"
                      >
                        <button
                          type="button"
                          onClick={() => setOpenDoc(doc)}
                          className="text-left w-full group"
                        >
                          <p
                            className="font-serif mb-1"
                            style={{
                              fontSize: "var(--text-body-v4)",
                              lineHeight: "var(--text-body-v4--line-height)",
                              color: "var(--color-ink-v4)",
                              fontWeight: 600,
                            }}
                          >
                            <span className="group-hover:underline decoration-1 underline-offset-4">
                              {doc.label[lang] || doc.label.en}
                            </span>
                            {year && (
                              <span
                                className="font-mono ml-2"
                                style={{
                                  fontSize: "var(--text-mono-sm)",
                                  color: "var(--color-ink-3-v4)",
                                  fontWeight: 400,
                                }}
                              >
                                {year}
                              </span>
                            )}
                          </p>
                          {doc.source_label && (
                            <p
                              className="font-sans"
                              style={{
                                fontSize: "var(--text-ui-sm)",
                                color: "var(--color-ink-3-v4)",
                              }}
                            >
                              {t("detail.v4.viaSource", { source: doc.source_label })}
                              <span
                                aria-hidden="true"
                                className="ml-2"
                                style={{ color: "var(--color-link)" }}
                              >
                                →
                              </span>
                            </p>
                          )}
                        </button>
                      </li>
                    )
                  })}
                </ul>
              ) : (
                <p
                  className="font-serif italic"
                  style={{
                    fontSize: "var(--text-body-v4)",
                    color: "var(--color-ink-2-v4)",
                  }}
                >
                  {t("detail.breakdown.unavailable")}
                </p>
              )}

              {/* EIN / registration ID — bottom of rail, in mono like a citation */}
              {charity.registration_id && (
                <p
                  className="font-mono mt-6 pt-6"
                  style={{
                    borderTop: "1px solid var(--color-rule-soft-v4)",
                    fontSize: "var(--text-mono-sm)",
                    color: "var(--color-ink-2-v4)",
                  }}
                >
                  {regPrefix} {charity.registration_id}
                </p>
              )}
            </div>
          </aside>
        </div>

        {/* ============= HOW TO GIVE ============= */}
        {charity.donation_url && (
          <section
            className="mt-16 lg:mt-24 pt-14 max-w-[640px]"
            style={{ borderTop: "1px solid var(--color-rule-v4)" }}
          >
            <h2
              className="font-serif mb-6"
              style={{
                fontSize: "var(--text-display-md)",
                lineHeight: "var(--text-display-md--line-height)",
                fontWeight: 400,
                letterSpacing: "-0.01em",
                color: "var(--color-ink-v4)",
              }}
            >
              {t("detail.v4.howToGive")}
            </h2>
            <p
              className="font-serif mb-8"
              style={{
                fontSize: "var(--text-body-lg)",
                lineHeight: "var(--text-body-lg--line-height)",
                color: "var(--color-ink-v4)",
              }}
            >
              {t("detail.v4.howToGiveBody", { hostname: donationHost })}
            </p>
            <button
              type="button"
              onClick={() => setDonateOpen(true)}
              className="font-sans inline-flex items-center gap-3 px-8 py-4 transition-colors duration-150"
              style={{
                fontSize: "var(--text-ui-md)",
                fontWeight: 500,
                color: "var(--color-ink-v4)",
                background: "transparent",
                border: "1px solid var(--color-ink-v4)",
                borderRadius: "var(--radius-ui-v4)",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = "var(--color-link)"
                e.currentTarget.style.borderColor = "var(--color-link)"
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = "var(--color-ink-v4)"
                e.currentTarget.style.borderColor = "var(--color-ink-v4)"
              }}
            >
              {t("detail.v4.howToGiveCta", { hostname: donationHost })}
              <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
            </button>
            <p
              className="font-sans mt-3"
              style={{
                fontSize: "var(--text-ui-sm)",
                color: "var(--color-ink-3-v4)",
              }}
            >
              {t("detail.donate.microcopy")}
            </p>
          </section>
        )}

        {/* ============= WHERE THE MONEY GOES ============= */}
        <section
          className="mt-16 lg:mt-24 pt-14 max-w-[720px]"
          style={{ borderTop: "1px solid var(--color-rule-v4)" }}
        >
          <h2
            className="font-serif mb-8"
            style={{
              fontSize: "var(--text-display-md)",
              lineHeight: "var(--text-display-md--line-height)",
              fontWeight: 400,
              letterSpacing: "-0.01em",
              color: "var(--color-ink-v4)",
            }}
          >
            {t("charity.moneyGoes")}
          </h2>
          <MoneyBreakdown
            data={charity.money_breakdown}
            totalRevenueUsd={charity.total_revenue_usd}
            fallbackYear={
              charity.last_filed_date ? Number(charity.last_filed_date.slice(0, 4)) : null
            }
          />
        </section>

        {/* ============= METHODOLOGY ============= */}
        {methodology && (
          <section
            className="mt-16 lg:mt-24 pt-14 max-w-[640px]"
            style={{ borderTop: "1px solid var(--color-rule-v4)" }}
          >
            <h2
              className="font-serif mb-6"
              style={{
                fontSize: "var(--text-display-md)",
                lineHeight: "var(--text-display-md--line-height)",
                fontWeight: 400,
                letterSpacing: "-0.01em",
                color: "var(--color-ink-v4)",
              }}
            >
              {t("detail.methodology")}
            </h2>
            <p
              className="font-serif italic"
              style={{
                fontSize: "var(--text-body-lg)",
                lineHeight: "var(--text-body-lg--line-height)",
                color: "var(--color-ink-2-v4)",
              }}
            >
              {methodology}
            </p>
          </section>
        )}

        {/* ============= PRESS MENTIONS ============= */}
        {charity.news_mentions.length > 0 && (
          <section
            className="mt-16 lg:mt-24 pt-14 max-w-[720px]"
            style={{ borderTop: "1px solid var(--color-rule-v4)" }}
          >
            <h2
              className="font-serif mb-8"
              style={{
                fontSize: "var(--text-display-md)",
                lineHeight: "var(--text-display-md--line-height)",
                fontWeight: 400,
                letterSpacing: "-0.01em",
                color: "var(--color-ink-v4)",
              }}
            >
              {t("charity.press")}
            </h2>
            <ul>
              {charity.news_mentions.map((mention, i) => (
                <li
                  key={mention.url}
                  className="py-4"
                  style={
                    i < charity.news_mentions.length - 1
                      ? { borderBottom: "1px solid var(--color-rule-soft-v4)" }
                      : undefined
                  }
                >
                  <a
                    href={mention.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    lang={mention.language}
                    className="block group"
                  >
                    <p
                      className="font-sans uppercase mb-1"
                      style={{
                        fontSize: "var(--text-ui-sm)",
                        letterSpacing: "0.12em",
                        color: "var(--color-ink-3-v4)",
                        fontWeight: 500,
                      }}
                    >
                      {mention.publisher}
                      {mention.published_date && (
                        <>
                          <span className="mx-2">·</span>
                          <span className="font-mono">{mention.published_date}</span>
                        </>
                      )}
                    </p>
                    <p
                      className="font-serif group-hover:underline decoration-1 underline-offset-4"
                      style={{
                        fontSize: "var(--text-body-v4)",
                        lineHeight: "var(--text-body-v4--line-height)",
                        color: "var(--color-ink-v4)",
                      }}
                    >
                      {mention.title}
                    </p>
                  </a>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>

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
    </main>
  )
}

