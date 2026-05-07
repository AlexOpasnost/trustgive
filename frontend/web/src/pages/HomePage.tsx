/**
 * HomePage — restructured per DESIGN.md v2.0 §C.
 *
 * New section order:
 *   1. Hero (unchanged from v1.1)
 *   2. NEW: Featured charities — 6 CharityCard v2 in a responsive grid (1/2/3 cols)
 *   3. Editorial prose
 *   4. Stats
 *   5. Sources marquee
 *   6. Browse by cause
 *   7. Bottom CTA
 *
 * Featured strip renders only when `useFeaturedCharities()` returns ≥3 results
 * (DESIGN.md §G.2 cold-start fallback). Below that, the section unmounts and
 * the homepage falls back to the v1.1 manifesto-only flow.
 */

import { ArrowRight01Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { CharityCard } from "@/components/charity/CharityCard"
import { Button } from "@/components/ui/Button"
import { GenerativeShape } from "@/components/ui/GenerativeShape"
import { Reveal } from "@/components/ui/Reveal"
import { useFeaturedCharities } from "@/lib/queries"

const STATS: { figure: string; labelKey: string }[] = [
  { figure: "1.2M", labelKey: "home.stats.charities" },
  { figure: "0%", labelKey: "home.stats.fee" },
  { figure: "0", labelKey: "home.stats.tips" },
  { figure: "5", labelKey: "home.stats.sources" },
]

const CAUSES: { slug: string; nameKey: string }[] = [
  { slug: "animals", nameKey: "Animals welfare" },
  { slug: "children", nameKey: "Children + youth" },
  { slug: "climate", nameKey: "Climate + environment" },
  { slug: "education", nameKey: "Education" },
  { slug: "health", nameKey: "Health + medicine" },
  { slug: "refugees", nameKey: "Refugees + humanitarian" },
  { slug: "russia", nameKey: "Russia (curated)" },
]

const REGISTRIES: string[] = [
  "IRS Form 990",
  "UK Charity Commission",
  "Минюст СОНКО",
  "BBB Wise Giving",
  "GiveWell",
  "ProPublica Nonprofit Explorer",
  "Every.org",
  "CharityBase",
]

/**
 * Skeleton card placeholder used while featured charities load.
 * Matches CharityCard v2 dimensions so the layout doesn't shift on hydration.
 */
function FeaturedCardSkeleton() {
  return (
    <div className="bg-surface border border-rule rounded-md p-6 min-h-[180px]">
      <div className="flex items-start gap-5">
        <div className="skeleton w-12 h-12 rounded-md" />
        <div className="flex-1 space-y-3">
          <div className="skeleton h-5 w-3/4" />
          <div className="skeleton h-4 w-full" />
          <div className="skeleton h-4 w-5/6" />
          <div className="skeleton h-3 w-1/2 mt-4" />
        </div>
      </div>
    </div>
  )
}

function FeaturedSection() {
  const { t } = useTranslation()
  const { data, isLoading } = useFeaturedCharities()

  if (isLoading) {
    return (
      <section className="border-b border-rule">
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-16 lg:py-24">
          <p className="text-caption uppercase tracking-widest text-ink-3 font-medium mb-4">
            {t("homepage.featured.eyebrow")}
          </p>
          <h2
            className="font-serif text-ink mb-10"
            style={{
              fontSize: "clamp(28px, 3.5vw, 40px)",
              fontWeight: 400,
              letterSpacing: "-0.01em",
              lineHeight: 1.2,
            }}
          >
            {t("homepage.featured.title")}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <FeaturedCardSkeleton key={i} />
            ))}
          </div>
        </div>
      </section>
    )
  }

  // §G.2 cold-start fallback: section unmounts entirely if <3 results.
  if (!data || data.length < 3) {
    return null
  }

  const charities = data.slice(0, 6)

  return (
    <section className="border-b border-rule">
      <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-16 lg:py-24">
        <Reveal>
          <p className="text-caption uppercase tracking-widest text-ink-3 font-medium mb-4">
            {t("homepage.featured.eyebrow")}
          </p>
          <h2
            className="font-serif text-ink mb-3"
            style={{
              fontSize: "clamp(28px, 3.5vw, 40px)",
              fontWeight: 400,
              letterSpacing: "-0.01em",
              lineHeight: 1.2,
            }}
          >
            {t("homepage.featured.title")}
          </h2>
          <p className="text-body text-ink-2 mb-10 max-w-2xl">
            {t("homepage.featured.subtitle")}
          </p>
        </Reveal>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {charities.map((charity, i) => (
            <Reveal key={charity.slug} delay={i * 0.05}>
              <CharityCard charity={charity} />
            </Reveal>
          ))}
        </div>

        <div className="mt-10 text-center">
          <Link
            to="/charities"
            className="inline-flex items-center gap-1.5 text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("homepage.featured.seeAll")}
            <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
          </Link>
        </div>
      </div>
    </section>
  )
}

export function HomePage() {
  const { t } = useTranslation()

  return (
    <>
      {/* === HERO === */}
      <section className="border-b border-rule">
        <div className="max-w-(--container-wide) mx-auto px-6 lg:px-12 pt-20 lg:pt-32 pb-16 lg:pb-24">
          <div className="grid lg:grid-cols-12 gap-8 lg:gap-12 items-center">
            <Reveal className="lg:col-span-7">
              <h1
                className="font-serif text-ink"
                style={{
                  fontSize: "clamp(40px, 6vw, 84px)",
                  lineHeight: 1.05,
                  letterSpacing: "-0.02em",
                  fontWeight: 400,
                }}
              >
                {t("home.headline")}
              </h1>
              <p className="mt-8 text-h4 leading-relaxed text-ink-2 max-w-2xl">
                {t("home.subhead")}
              </p>

              <div className="mt-12 flex flex-wrap items-center gap-6">
                <Button as="a" href="/charities" variant="primary" size="lg">
                  {t("home.exploreCatalog")}
                  <HugeiconsIcon icon={ArrowRight01Icon} size={16} aria-hidden="true" />
                </Button>
                <Link
                  to="/methodology"
                  className="text-body text-ink-2 hover:text-ink underline-offset-4 underline decoration-rule hover:decoration-ink"
                >
                  {t("home.howWeVerify")}
                </Link>
              </div>
            </Reveal>

            <Reveal className="lg:col-span-5" delay={0.15}>
              <GenerativeShape className="w-full max-w-md mx-auto" />
            </Reveal>
          </div>
        </div>
      </section>

      {/* === FEATURED CHARITIES (NEW) === */}
      <FeaturedSection />

      {/* === EDITORIAL PROSE === */}
      <section className="border-b border-rule">
        <div className="max-w-(--container-narrow) mx-auto px-6 py-24 lg:py-32">
          <Reveal>
            <p className="text-caption uppercase tracking-widest text-ink-3 font-medium mb-8">
              {t("home.editorial.eyebrow")}
            </p>
            <h2
              className="font-serif text-ink mb-10"
              style={{
                fontSize: "clamp(32px, 4vw, 48px)",
                lineHeight: 1.15,
                fontWeight: 400,
                letterSpacing: "-0.01em",
              }}
            >
              {t("home.editorial.title")}
            </h2>
            <div
              className="space-y-6 font-serif text-ink-2"
              style={{ fontSize: "20px", lineHeight: "34px" }}
            >
              <p>{t("home.editorial.p1")}</p>
              <p>{t("home.editorial.p2")}</p>
              <p>{t("home.editorial.p3")}</p>
            </div>
            <Link
              to="/methodology"
              className="inline-flex items-center gap-2 mt-12 text-body text-ink underline-offset-4 underline decoration-clay hover:decoration-ink"
            >
              {t("home.editorial.cta")}
              <HugeiconsIcon icon={ArrowRight01Icon} size={14} />
            </Link>
          </Reveal>
        </div>
      </section>

      {/* === STATS === */}
      <section className="border-b border-rule">
        <div className="max-w-(--container-wide) mx-auto px-6 lg:px-12 py-16 lg:py-24">
          <Reveal>
            <p className="text-caption uppercase tracking-widest text-ink-3 font-medium mb-10">
              {t("home.stats.eyebrow")}
            </p>
          </Reveal>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-y-12 gap-x-8">
            {STATS.map((stat, i) => (
              <Reveal key={stat.figure} delay={i * 0.08}>
                <div className="border-l-2 border-ink pl-5">
                  <div
                    className="font-mono text-ink"
                    style={{
                      fontSize: "clamp(48px, 6vw, 88px)",
                      lineHeight: 0.95,
                      letterSpacing: "-0.04em",
                      fontWeight: 500,
                    }}
                  >
                    {stat.figure}
                  </div>
                  <div className="mt-3 text-body-sm text-ink-2 max-w-[180px]">
                    {t(stat.labelKey)}
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* === SOURCES MARQUEE === */}
      <section className="border-b border-rule overflow-hidden bg-surface">
        <div className="py-10">
          <Reveal className="max-w-(--container-wide) mx-auto px-6 lg:px-12 mb-6">
            <p className="text-caption uppercase tracking-widest text-ink-3 font-medium">
              {t("home.sources.eyebrow")}
            </p>
          </Reveal>
          <div className="flex gap-12 px-12 animate-marquee whitespace-nowrap">
            {[...REGISTRIES, ...REGISTRIES].map((reg, i) => (
              <span
                key={i}
                className="font-serif text-h2 text-ink-3"
                style={{ fontWeight: 400 }}
              >
                {reg}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* === BROWSE BY CAUSE === */}
      <section className="border-b border-rule">
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-24">
          <Reveal>
            <p className="text-caption uppercase tracking-widest text-ink-3 font-medium mb-4">
              {t("home.causes.eyebrow")}
            </p>
            <h2
              className="font-serif text-ink mb-12"
              style={{
                fontSize: "clamp(32px, 4vw, 48px)",
                fontWeight: 400,
                letterSpacing: "-0.01em",
              }}
            >
              {t("home.causes.title")}
            </h2>
          </Reveal>
          <div className="divide-y divide-rule border-y border-rule">
            {CAUSES.map((c, i) => (
              <Reveal key={c.slug} delay={i * 0.05}>
                <Link
                  to={`/charities?cause=${encodeURIComponent(c.slug)}`}
                  className="flex items-center justify-between py-5 group hover:px-2 transition-all"
                >
                  <span className="font-serif text-h2 text-ink" style={{ fontWeight: 400 }}>
                    {c.nameKey}
                  </span>
                  <span className="text-ink-3 group-hover:text-ink transition-colors">
                    <HugeiconsIcon icon={ArrowRight01Icon} size={20} />
                  </span>
                </Link>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* === BOTTOM CTA === */}
      <section>
        <div className="max-w-(--container-narrow) mx-auto px-6 py-24 text-center">
          <Reveal>
            <h2
              className="font-serif text-ink mb-6"
              style={{
                fontSize: "clamp(28px, 3.5vw, 40px)",
                fontWeight: 400,
                letterSpacing: "-0.01em",
                lineHeight: 1.2,
              }}
            >
              {t("home.bottomCta.title")}
            </h2>
            <p className="text-body text-ink-2 mb-10 max-w-md mx-auto">
              {t("home.bottomCta.body")}
            </p>
            <Button as="a" href="/charities" variant="primary" size="lg">
              {t("home.exploreCatalog")}
              <HugeiconsIcon icon={ArrowRight01Icon} size={16} aria-hidden="true" />
            </Button>
          </Reveal>
        </div>
      </section>
    </>
  )
}
