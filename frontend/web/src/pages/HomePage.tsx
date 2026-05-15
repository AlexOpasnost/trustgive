/**
 * HomePage — DESIGN_v4.md §6.1 (editorial line, 2026-05-15).
 *
 * v4 structure (replaces v3.0's three-card hero entirely):
 *   1. Type-first hero. Big Source Serif 4 italic headline. Photo is NOT
 *      above the fold — the page opens with words.
 *   2. Standfirst block clamped to a reading column.
 *   3. Three bucket SPREADS (not cards): each is a side-by-side editorial
 *      composition with the bucket photo on one side and the standfirst +
 *      "See all" link on the other. Photo alternates left/right per bucket
 *      so the page reads like a printed gatefold. Hairline rule between
 *      spreads; no card chrome.
 *
 * Mobile (<720px): each bucket spread stacks. Photo on top, text below.
 *
 * Photo handling: still uses useFeaturedCharities to surface a real charity
 * photo per bucket (via /img/v1 Worker proxy + responsive srcset).
 */

import { ArrowRight01Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { PHOTO_WIDTHS, SRCSET_WIDTHS, buildSrcSet, wikimediaThumb } from "@/lib/image"
import { useFeaturedCharities } from "@/lib/queries"
import { useDocumentTitle } from "@/lib/useDocumentTitle"
import type { Bucket, CharitySummary } from "@/types/api"

const BUCKETS: Bucket[] = ["people", "planet", "animals"]

/**
 * BucketSpread — one row of the editorial section. Photo on one side, text
 * on the other. The `align` prop controls which side the photo lands on at
 * ≥lg breakpoint; below that everything stacks photo-on-top.
 */
function BucketSpread({ bucket, align }: { bucket: Bucket; align: "left" | "right" }) {
  const { t } = useTranslation()
  const { data, isLoading } = useFeaturedCharities({ bucket })

  const featured: CharitySummary[] = data?.featured ?? []
  const count = data?.total_count ?? 0
  const first = featured[0]
  const rawPhoto = first?.hero_photo_url ?? null

  const photoUrl = rawPhoto ? wikimediaThumb(rawPhoto, PHOTO_WIDTHS.bucketHero) : null
  const photoSrcSet = rawPhoto ? buildSrcSet(rawPhoto, SRCSET_WIDTHS.bucketHero) : ""

  const bucketLabelEn = bucket === "people" ? "People" : bucket === "planet" ? "Planet" : "Animals"
  const bucketLabelRu = bucket === "people" ? "Людям" : bucket === "planet" ? "Планете" : "Животным"
  const lang = t("__lang", { defaultValue: "" }) // never resolves; used to bind to i18n
  void lang
  const bucketLabel = t(`homepage.bucket.${bucket}.label`)
  void bucketLabelEn
  void bucketLabelRu

  const standfirst = t(`home.v4.bucket.${bucket}.standfirst`)
  const seeAll = t("home.v4.seeAll", { count, bucket: bucketLabel })

  // Photo column. Aspect 4:3 to read as editorial illustration, not hero.
  const photoNode = (
    <div className="relative aspect-[4/3] overflow-hidden bg-stone-100">
      {photoUrl ? (
        <img
          src={photoUrl}
          srcSet={photoSrcSet}
          sizes="(min-width: 1024px) 48vw, 100vw"
          alt=""
          loading="lazy"
          decoding="async"
          className="absolute inset-0 h-full w-full object-cover object-center"
        />
      ) : (
        <div
          aria-hidden="true"
          className="absolute inset-0"
          style={{ background: "var(--color-paper-2-v4)" }}
        />
      )}
      {isLoading && <div className="absolute inset-0 skeleton" />}
    </div>
  )

  // Text column. Eyebrow + standfirst + brick link.
  const textNode = (
    <div className="flex flex-col justify-center py-8 lg:py-12">
      <p
        className="font-sans uppercase mb-6"
        style={{
          fontSize: "var(--text-ui-sm)",
          lineHeight: "var(--text-ui-sm--line-height)",
          letterSpacing: "0.12em",
          color: "var(--color-ink-3-v4)",
          fontWeight: 500,
        }}
      >
        {bucketLabel} · {count} {bucket === "people" ? "charities" : bucket === "planet" ? "charities" : "charities"}
      </p>
      <p
        className="font-serif mb-8 max-w-[44ch]"
        style={{
          fontSize: "var(--text-body-lg)",
          lineHeight: "var(--text-body-lg--line-height)",
          color: "var(--color-ink-v4)",
        }}
      >
        {standfirst}
      </p>
      <Link
        to={`/charities?bucket=${bucket}`}
        className="font-sans inline-flex items-center gap-2 self-start group"
        style={{
          fontSize: "var(--text-ui-md)",
          lineHeight: "var(--text-ui-md--line-height)",
          color: "var(--color-link)",
          fontWeight: 500,
        }}
      >
        <span className="underline decoration-1 underline-offset-4 group-hover:no-underline">
          {seeAll}
        </span>
        <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
      </Link>
    </div>
  )

  return (
    <section
      aria-label={`${bucketLabel} — ${count}`}
      className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-stretch py-12 lg:py-20"
    >
      {align === "left" ? (
        <>
          {photoNode}
          {textNode}
        </>
      ) : (
        <>
          <div className="order-1 lg:order-2">{photoNode}</div>
          <div className="order-2 lg:order-1">{textNode}</div>
        </>
      )}
    </section>
  )
}

export function HomePage() {
  const { t } = useTranslation()
  // Homepage owns the brand title — every other route mounts its own.
  useDocumentTitle("TrustGive — A discovery archive of verified charities")

  return (
    <main style={{ background: "var(--color-paper-v4)", color: "var(--color-ink-v4)" }}>
      {/* =================== HERO: type-first ===================== */}
      <section className="px-6 lg:px-12 pt-16 lg:pt-28 pb-12 lg:pb-20 max-w-[1280px] mx-auto">
        <p
          className="font-sans uppercase mb-10 lg:mb-16"
          style={{
            fontSize: "var(--text-ui-sm)",
            lineHeight: "var(--text-ui-sm--line-height)",
            letterSpacing: "0.16em",
            color: "var(--color-ink-3-v4)",
            fontWeight: 500,
          }}
        >
          {t("home.v4.eyebrow")}
        </p>

        <h1
          className="font-serif"
          style={{
            // Responsive clamp — 88px is too big on phones.
            fontSize: "clamp(40px, 7vw, 88px)",
            lineHeight: 1.05,
            fontWeight: 400,
            fontStyle: "italic",
            letterSpacing: "-0.015em",
            color: "var(--color-ink-v4)",
          }}
        >
          {t("home.v4.headline1")}
          <br />
          {t("home.v4.headline2")}
          <br />
          {t("home.v4.headline3")}
        </h1>

        <div
          className="mt-12 lg:mt-16"
          style={{ borderTop: "1px solid var(--color-rule-v4)" }}
        />

        <p
          className="font-serif italic mt-10 lg:mt-14"
          style={{
            fontSize: "var(--text-dek)",
            lineHeight: "var(--text-dek--line-height)",
            color: "var(--color-ink-2-v4)",
          }}
        >
          {t("home.v4.dek")}
        </p>

        <p
          className="font-serif mt-6 lg:mt-8 max-w-[640px]"
          style={{
            fontSize: "var(--text-body-lg)",
            lineHeight: "var(--text-body-lg--line-height)",
            color: "var(--color-ink-v4)",
          }}
        >
          {t("home.v4.standfirst")}
        </p>
      </section>

      {/* =================== BUCKETS: editorial spreads ===================== */}
      <div className="px-6 lg:px-12 max-w-[1280px] mx-auto">
        {BUCKETS.map((bucket, i) => (
          <div
            key={bucket}
            style={i === 0 ? { borderTop: "1px solid var(--color-rule-v4)" } : undefined}
          >
            {i > 0 && (
              <div style={{ borderTop: "1px solid var(--color-rule-v4)" }} />
            )}
            <BucketSpread bucket={bucket} align={i % 2 === 0 ? "left" : "right"} />
          </div>
        ))}
      </div>

      {/* =================== METHODOLOGY KICKER ===================== */}
      <section
        className="px-6 lg:px-12 max-w-[1280px] mx-auto py-16 lg:py-24"
        style={{ borderTop: "1px solid var(--color-rule-v4)" }}
      >
        <Link
          to="/methodology"
          className="font-sans inline-flex items-center gap-2 group"
          style={{
            fontSize: "var(--text-ui-md)",
            lineHeight: "var(--text-ui-md--line-height)",
            color: "var(--color-link)",
            fontWeight: 500,
          }}
        >
          <span className="underline decoration-1 underline-offset-4 group-hover:no-underline">
            {t("home.editorial.cta")}
          </span>
          <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
        </Link>
      </section>
    </main>
  )
}
