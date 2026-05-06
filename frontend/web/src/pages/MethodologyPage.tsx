import { useTranslation } from "react-i18next"

export function MethodologyPage() {
  const { t } = useTranslation()
  const today = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })

  return (
    <article className="max-w-(--container-narrow) mx-auto px-6 py-24 font-serif">
      <header className="mb-12">
        <h1 className="text-display font-normal leading-tight text-ink mb-4">
          {t("methodology.title")}
        </h1>
        <p className="text-h4 leading-relaxed text-ink-2 max-w-2xl">{t("methodology.lead")}</p>
        <p className="text-caption text-ink-3 mt-4 font-sans font-mono">
          {t("methodology.lastReviewed", { date: today })}
        </p>
      </header>

      <hr className="border-rule my-12" />

      <section className="mb-16">
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">
          {t("methodology.verifiedMeansTitle")}
        </h2>
        <p className="text-body leading-relaxed text-ink-2" style={{ fontSize: "19px", lineHeight: "32px" }}>
          {t("methodology.verifiedMeansBody")}
        </p>
      </section>

      <hr className="border-rule my-12" />

      <section className="mb-16">
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">
          {t("methodology.doNotVerifyTitle")}
        </h2>
        <p className="text-body leading-relaxed text-ink-2" style={{ fontSize: "19px", lineHeight: "32px" }}>
          {t("methodology.doNotVerifyBody")}
        </p>
      </section>

      <hr className="border-rule my-12" />

      <section className="mb-16">
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">
          {t("methodology.complianceTitle")}
        </h2>
        <p className="text-body leading-relaxed text-ink-2" style={{ fontSize: "19px", lineHeight: "32px" }}>
          {t("methodology.complianceBody")}
        </p>
        <ul className="mt-6 space-y-3 list-disc list-inside text-body text-ink-2 font-sans" style={{ fontSize: "17px", lineHeight: "28px" }}>
          <li>{t("methodology.complianceItem1")}</li>
          <li>{t("methodology.complianceItem2")}</li>
          <li>{t("methodology.complianceItem3")}</li>
          <li>{t("methodology.complianceItem4")}</li>
        </ul>
        <p className="text-body leading-relaxed text-ink-2 mt-6" style={{ fontSize: "19px", lineHeight: "32px" }}>
          {t("methodology.complianceFooter")}
        </p>
      </section>

      <hr className="border-rule my-12" />

      <section>
        <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">
          {t("methodology.deeperTitle")}
        </h2>
        <p className="text-body leading-relaxed text-ink-2" style={{ fontSize: "19px", lineHeight: "32px" }}>
          {t("methodology.deeperBody")}
        </p>
      </section>
    </article>
  )
}
