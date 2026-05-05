import { HugeiconsIcon } from "@hugeicons/react"
import {
  ArrowRight01Icon,
  FileVerifiedIcon,
  Tick02Icon,
  LinkSquare02Icon,
} from "@hugeicons/core-free-icons"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

const FEATURED_CAUSES: { slug: string; nameKey: string; count: string }[] = [
  { slug: "animals", nameKey: "Animals", count: "212" },
  { slug: "children", nameKey: "Children", count: "1,844" },
  { slug: "climate", nameKey: "Climate", count: "92" },
  { slug: "education", nameKey: "Education", count: "2,103" },
  { slug: "health", nameKey: "Health", count: "3,415" },
  { slug: "refugees", nameKey: "Refugees", count: "189" },
  { slug: "russia", nameKey: "Russia (curated)", count: "30" },
]

export function HomePage() {
  const { t } = useTranslation()

  return (
    <>
      <section className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-24 text-center">
        <h1 className="text-display font-semibold leading-tight text-ink mb-6 max-w-3xl mx-auto">
          {t("home.headline")}
        </h1>
        <p className="text-h4 leading-relaxed text-ink-2 max-w-2xl mx-auto mb-12">
          {t("home.subhead")}
        </p>

        <div className="inline-flex flex-col items-center gap-2 bg-verified-soft border border-verified rounded-lg px-8 py-6 mb-12">
          <span className="font-mono text-display text-verified leading-none">0%</span>
          <span className="text-body text-ink-2">{t("home.noFee")}</span>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/charities"
            className="inline-flex items-center gap-2 bg-verified text-verified-on px-6 py-3 rounded-md text-body font-medium hover:opacity-90"
          >
            {t("home.exploreCatalog")}
            <HugeiconsIcon icon={ArrowRight01Icon} size={16} />
          </Link>
          <Link
            to="/methodology"
            className="text-body text-ink-2 hover:text-ink underline-offset-4 hover:underline"
          >
            {t("home.howWeVerify")} →
          </Link>
        </div>
      </section>

      <hr className="border-rule max-w-(--container-default) mx-auto" />

      <section className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-16">
        <h2 className="text-h2 font-semibold text-ink mb-8">{t("home.browseByCause")}</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {FEATURED_CAUSES.map((c) => (
            <Link
              key={c.slug}
              to={`/charities?cause=${encodeURIComponent(c.slug)}`}
              className="border border-rule rounded-md px-4 py-5 bg-surface hover:bg-paper transition-colors"
            >
              <div className="text-h4 font-semibold text-ink">{c.nameKey}</div>
              <div className="font-mono text-body-sm text-ink-3 mt-1">{c.count}</div>
            </Link>
          ))}
        </div>
      </section>

      <hr className="border-rule max-w-(--container-default) mx-auto" />

      <section className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-16">
        <h2 className="text-h2 font-semibold text-ink mb-8">{t("home.verifySection.title")}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="border border-rule rounded-md p-6 bg-surface">
            <HugeiconsIcon icon={FileVerifiedIcon} size={24} className="text-verified mb-3" />
            <h3 className="text-h4 font-semibold text-ink mb-2">
              {t("home.verifySection.registry.title")}
            </h3>
            <p className="text-body-sm text-ink-2 mb-4">{t("home.verifySection.registry.body")}</p>
            <Link to="/methodology" className="text-body-sm text-verified hover:underline">
              {t("home.verifySection.registry.link")} →
            </Link>
          </div>

          <div className="border border-rule rounded-md p-6 bg-surface">
            <HugeiconsIcon icon={Tick02Icon} size={24} className="text-verified mb-3" />
            <h3 className="text-h4 font-semibold text-ink mb-2">
              {t("home.verifySection.filings.title")}
            </h3>
            <p className="text-body-sm text-ink-2">{t("home.verifySection.filings.body")}</p>
          </div>

          <div className="border border-rule rounded-md p-6 bg-surface">
            <HugeiconsIcon icon={LinkSquare02Icon} size={24} className="text-verified mb-3" />
            <h3 className="text-h4 font-semibold text-ink mb-2">
              {t("home.verifySection.outbound.title")}
            </h3>
            <p className="text-body-sm text-ink-2">{t("home.verifySection.outbound.body")}</p>
          </div>
        </div>
      </section>
    </>
  )
}
