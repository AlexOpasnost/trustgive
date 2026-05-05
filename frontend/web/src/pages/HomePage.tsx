import { HugeiconsIcon } from "@hugeicons/react"
import { ArrowRight01Icon } from "@hugeicons/core-free-icons"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { GenerativeShape } from "@/components/ui/GenerativeShape"
import { Reveal } from "@/components/ui/Reveal"

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

export function HomePage() {
  const { t } = useTranslation()

  return (
    <>
      {/* === HERO — asymmetric 7/5 grid, serif display, generative shape === */}
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
                <Link
                  to="/charities"
                  className="inline-flex items-center gap-2 bg-ink text-paper px-6 py-3 rounded-md text-body font-medium hover:bg-ink-2 transition-colors"
                >
                  {t("home.exploreCatalog")}
                  <HugeiconsIcon icon={ArrowRight01Icon} size={16} />
                </Link>
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

      {/* === STATS — full-bleed, oversized Geist Mono, editorial dividers === */}
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

      {/* === EDITORIAL PROSE — long-form serif, narrow column === */}
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
            <div className="space-y-6 font-serif text-ink-2" style={{ fontSize: "20px", lineHeight: "34px" }}>
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

      {/* === SOURCES MARQUEE — registries we draw from === */}
      <section className="border-b border-rule overflow-hidden bg-surface">
        <div className="py-10">
          <Reveal className="max-w-(--container-wide) mx-auto px-6 lg:px-12 mb-6">
            <p className="text-caption uppercase tracking-widest text-ink-3 font-medium">
              {t("home.sources.eyebrow")}
            </p>
          </Reveal>
          <div className="flex gap-12 px-12 animate-marquee whitespace-nowrap">
            {[...REGISTRIES, ...REGISTRIES].map((reg, i) => (
              <span key={i} className="font-serif text-h2 text-ink-3" style={{ fontWeight: 400 }}>
                {reg}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* === BROWSE BY CAUSE — refined editorial list, not card grid === */}
      <section className="border-b border-rule">
        <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-24">
          <Reveal>
            <p className="text-caption uppercase tracking-widest text-ink-3 font-medium mb-4">
              {t("home.causes.eyebrow")}
            </p>
            <h2 className="font-serif text-ink mb-12" style={{ fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 400, letterSpacing: "-0.01em" }}>
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

      {/* === BOTTOM CTA — quiet === */}
      <section>
        <div className="max-w-(--container-narrow) mx-auto px-6 py-24 text-center">
          <Reveal>
            <h2 className="font-serif text-ink mb-6" style={{ fontSize: "clamp(28px, 3.5vw, 40px)", fontWeight: 400, letterSpacing: "-0.01em", lineHeight: 1.2 }}>
              {t("home.bottomCta.title")}
            </h2>
            <p className="text-body text-ink-2 mb-10 max-w-md mx-auto">
              {t("home.bottomCta.body")}
            </p>
            <Link
              to="/charities"
              className="inline-flex items-center gap-2 bg-ink text-paper px-6 py-3 rounded-md text-body font-medium hover:bg-ink-2 transition-colors"
            >
              {t("home.exploreCatalog")}
              <HugeiconsIcon icon={ArrowRight01Icon} size={16} />
            </Link>
          </Reveal>
        </div>
      </section>
    </>
  )
}
