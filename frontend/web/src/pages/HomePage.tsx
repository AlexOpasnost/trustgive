/**
 * HomePage — DESIGN.md v3.0 §A.
 *
 * v3.0 section order (replaces v2.0 entirely):
 *   1. THREE HERO BUCKET CARDS (above-the-fold, full-bleed photo, 70vh tall)
 *      — calls useFeaturedCharities({bucket}) for each bucket to get one
 *        representative photo URL + the verified-charities count.
 *   2. Manifesto block (cream/serif, demoted below the buckets)
 *      — preserves ONE editorial paragraph from v2.0 + a Methodology link.
 *
 * Footer is rendered by Layout, not here.
 *
 * Above-the-fold render path:
 *   - Tan-Stack Query fetches /api/charities/featured/?bucket=people (and animals + planet)
 *     in parallel.
 *   - While loading: 3 skeleton cards with neutral surface.
 *   - On success: pass first charity's hero_photo_url + count to <HeroBucketCard>.
 *   - If a bucket has 0 charities (shouldn't happen — backend seeded 19): the
 *     card is hidden.
 */

import { ArrowRight01Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { HeroBucketCard } from "@/components/home/HeroBucketCard"
import { Reveal } from "@/components/ui/Reveal"
import { PHOTO_WIDTHS, SRCSET_WIDTHS, buildSrcSet, wikimediaThumb } from "@/lib/image"
import { useFeaturedCharities } from "@/lib/queries"
import type { Bucket, CharitySummary } from "@/types/api"

const BUCKETS: Bucket[] = ["people", "animals", "planet"]

/**
 * Skeleton placeholder for a hero bucket card during initial load.
 * Same height as the real card to avoid layout shift.
 */
function HeroBucketSkeleton() {
  return (
    <div
      aria-hidden="true"
      className="
        relative overflow-hidden
        bg-stone-200
        min-h-[50vh] md:min-h-[60vh] lg:min-h-[70vh]
      "
    >
      <div className="absolute inset-0 skeleton" />
    </div>
  )
}

type BucketSlotProps = {
  bucket: Bucket
}

function BucketSlot({ bucket }: BucketSlotProps) {
  const { t } = useTranslation()
  const { data, isLoading, isError } = useFeaturedCharities({ bucket })

  if (isLoading) {
    return <HeroBucketSkeleton />
  }

  // v3.15: response envelope is { featured: [], total_count: N }. Earlier
  // versions used `count = data?.length` here — that returned the size of the
  // featured array (max 6), not the real catalog size. Now we use the explicit
  // total_count field from the API.
  const featured = data?.featured ?? []
  const count = data?.total_count ?? 0

  // Fail-soft: even if the featured fetch errors, render a card pointing at the
  // bucket with placeholder photo so the user still has the navigation anchor.
  // Hide only if we got an empty (0-charity) bucket.
  if (!isError && featured.length === 0 && count === 0) {
    return null
  }

  const first: CharitySummary | undefined = featured[0]
  const rawPhoto = first?.hero_photo_url ?? null
  const photoUrl = rawPhoto ? wikimediaThumb(rawPhoto, PHOTO_WIDTHS.bucketHero) : null
  const photoSrcSet = rawPhoto ? buildSrcSet(rawPhoto, SRCSET_WIDTHS.bucketHero) : ""

  // Subtitle: count is real-data driven. We pluralize naively for EN/RU via i18n.
  const subtitleKey =
    count === 0
      ? "homepage.bucket.subtitleEmpty"
      : count === 1
        ? "homepage.bucket.subtitleOne"
        : "homepage.bucket.subtitle"
  const label = t(`homepage.bucket.${bucket}.label`)
  const subtitle = t(subtitleKey, { count })

  return (
    <HeroBucketCard
      bucket={bucket}
      photoUrl={photoUrl}
      photoSrcSet={photoSrcSet}
      label={label}
      subtitle={subtitle}
      href={`/charities?bucket=${bucket}`}
      photoCredit=""
    />
  )
}

export function HomePage() {
  const { t } = useTranslation()

  return (
    <>
      {/* === HERO: 3 BUCKET CARDS (above-the-fold) === */}
      <section
        aria-label="Browse by cause"
        className="border-b border-rule"
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-0">
          {BUCKETS.map((bucket) => (
            <BucketSlot key={bucket} bucket={bucket} />
          ))}
        </div>
      </section>

      {/* === MANIFESTO (demoted below the buckets) === */}
      <section className="bg-paper">
        <div className="max-w-(--container-narrow) mx-auto px-6 py-20 lg:py-28">
          <Reveal>
            <p className="text-caption uppercase tracking-widest text-ink-3 font-medium mb-6">
              {t("home.editorial.eyebrow")}
            </p>
            <h2
              className="font-serif text-ink mb-8"
              style={{
                fontSize: "clamp(28px, 3.5vw, 40px)",
                lineHeight: 1.2,
                fontWeight: 600,
                letterSpacing: "-0.01em",
              }}
            >
              {t("home.editorial.title")}
            </h2>
            <p
              className="text-ink-2"
              style={{ fontSize: "18px", lineHeight: "30px" }}
            >
              {t("home.editorial.p1")}
            </p>
            <Link
              to="/methodology"
              className="inline-flex items-center gap-2 mt-10 text-body text-ink underline-offset-4 underline decoration-rule hover:decoration-ink"
            >
              {t("home.editorial.cta")}
              <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
            </Link>
          </Reveal>
        </div>
      </section>
    </>
  )
}
