import { useTranslation } from "react-i18next"

import { useDocumentTitle } from "@/lib/useDocumentTitle"

export function MethodologyPage() {
  const { t } = useTranslation()
  useDocumentTitle(t("methodology.title"))
  const today = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })

  return (
    <article className="max-w-(--container-narrow) mx-auto px-6 band font-serif">
      <header className="mb-12">
        {/* Was `font-normal` with `leading-tight`, so this page's title was the
            one page title on the site in light serif with its own line-height.
            Same element, same role as every other H1 — same treatment. */}
        <h1 className="text-display font-bold text-ink mb-4">{t("methodology.title")}</h1>
        <p className="text-lead text-ink-2 max-w-2xl">{t("methodology.lead")}</p>
        <p className="text-caption text-ink-3 mt-4 font-sans font-mono">
          {t("methodology.lastReviewed", { date: today })}
        </p>
      </header>

      <hr className="border-rule my-12" />

      <section className="mb-16">
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">
          {t("methodology.verifiedMeansTitle")}
        </h2>
        <p className="text-prose text-ink-2">
          {t("methodology.verifiedMeansBody")}
        </p>
      </section>

      <hr className="border-rule my-12" />

      {/* The catalogue policy. Stated here because it is the one editorial rule
          that changes what a visitor sees: organisations we could not confirm are
          absent entirely, so an empty search result may mean "not verified yet"
          rather than "does not exist". Leaving that unsaid would be its own kind
          of misdirection. */}
      <section className="mb-16">
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">
          {t("methodology.catalogueTitle")}
        </h2>
        <p className="text-prose text-ink-2">
          {t("methodology.catalogueBody")}
        </p>
        <p className="text-prose text-ink-2 mt-4">
          {t("methodology.catalogueBody2")}
        </p>
      </section>

      <hr className="border-rule my-12" />

      <section className="mb-16">
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">
          {t("methodology.doNotVerifyTitle")}
        </h2>
        <p className="text-prose text-ink-2">
          {t("methodology.doNotVerifyBody")}
        </p>
      </section>

      <hr className="border-rule my-12" />

      <section className="mb-16">
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">
          {t("methodology.complianceTitle")}
        </h2>
        <p className="text-prose text-ink-2">
          {t("methodology.complianceBody")}
        </p>
        <ul className="mt-6 space-y-3 list-disc list-inside text-prose-sm text-ink-2 font-sans">
          <li>{t("methodology.complianceItem1")}</li>
          <li>{t("methodology.complianceItem2")}</li>
          <li>{t("methodology.complianceItem3")}</li>
          <li>{t("methodology.complianceItem4")}</li>
        </ul>
        <p className="text-prose text-ink-2 mt-6">
          {t("methodology.complianceFooter")}
        </p>
      </section>

      <hr className="border-rule my-12" />

      <section>
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">
          {t("methodology.deeperTitle")}
        </h2>
        <p className="text-prose text-ink-2">
          {t("methodology.deeperBody")}
        </p>
      </section>
    </article>
  )
}
