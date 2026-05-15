/**
 * MethodologyPage — DESIGN_v4.md §5 (page measure: clamped to 640px, single
 * column, like a magazine essay).
 *
 * One family throughout (Source Serif 4), italic lead under the title,
 * hairline dividers between sections, no sans-serif h2s, drop cap on the
 * first paragraph. The compliance list is the only place where Inter
 * sneaks in — it's metadata, not body.
 */

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

  const sectionH2: React.CSSProperties = {
    fontSize: "var(--text-display-md)",
    lineHeight: "var(--text-display-md--line-height)",
    fontWeight: 400,
    letterSpacing: "-0.01em",
    color: "var(--color-ink-v4)",
  }
  const body: React.CSSProperties = {
    fontSize: "var(--text-body-lg)",
    lineHeight: "var(--text-body-lg--line-height)",
    color: "var(--color-ink-v4)",
  }
  const rule: React.CSSProperties = {
    borderTop: "1px solid var(--color-rule-v4)",
  }

  return (
    <main
      style={{ background: "var(--color-paper-v4)", color: "var(--color-ink-v4)" }}
    >
      <article className="max-w-[640px] mx-auto px-6 pt-16 lg:pt-24 pb-24 font-serif">
        <header className="mb-14">
          <h1
            style={{
              fontSize: "clamp(40px, 6vw, 64px)",
              lineHeight: 1.05,
              fontWeight: 400,
              letterSpacing: "-0.015em",
              color: "var(--color-ink-v4)",
            }}
          >
            {t("methodology.title")}
          </h1>
          <p
            className="italic mt-6"
            style={{
              fontSize: "var(--text-dek)",
              lineHeight: "var(--text-dek--line-height)",
              color: "var(--color-ink-2-v4)",
            }}
          >
            {t("methodology.lead")}
          </p>
          <p
            className="font-mono mt-8"
            style={{
              fontSize: "var(--text-mono-sm)",
              color: "var(--color-ink-3-v4)",
            }}
          >
            {t("methodology.lastReviewed", { date: today })}
          </p>
        </header>

        <hr style={rule} className="my-12" />

        <section className="mb-14">
          <h2 className="mb-6" style={sectionH2}>
            {t("methodology.verifiedMeansTitle")}
          </h2>
          <p className="v4-drop-cap" style={body}>
            {t("methodology.verifiedMeansBody")}
          </p>
        </section>

        <hr style={rule} className="my-12" />

        <section className="mb-14">
          <h2 className="mb-6" style={sectionH2}>
            {t("methodology.doNotVerifyTitle")}
          </h2>
          <p style={body}>{t("methodology.doNotVerifyBody")}</p>
        </section>

        <hr style={rule} className="my-12" />

        <section className="mb-14">
          <h2 className="mb-6" style={sectionH2}>
            {t("methodology.complianceTitle")}
          </h2>
          <p style={body}>{t("methodology.complianceBody")}</p>
          <ul
            className="mt-6 space-y-3 list-disc pl-6"
            style={{
              fontSize: "var(--text-body-v4)",
              lineHeight: "var(--text-body-v4--line-height)",
              color: "var(--color-ink-2-v4)",
            }}
          >
            <li>{t("methodology.complianceItem1")}</li>
            <li>{t("methodology.complianceItem2")}</li>
            <li>{t("methodology.complianceItem3")}</li>
            <li>{t("methodology.complianceItem4")}</li>
          </ul>
          <p className="mt-6" style={body}>
            {t("methodology.complianceFooter")}
          </p>
        </section>

        <hr style={rule} className="my-12" />

        <section>
          <h2 className="mb-6" style={sectionH2}>
            {t("methodology.deeperTitle")}
          </h2>
          <p style={body}>{t("methodology.deeperBody")}</p>
        </section>
      </article>
    </main>
  )
}
