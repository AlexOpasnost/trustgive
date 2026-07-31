/**
 * AboutPage — who runs this and on what terms.
 *
 * A directory whose only asset is trust cannot be anonymous. This page carries
 * the name, the reason, the funding position, the limits, and a way to report an
 * error. Copy is deliberately first-person and specific: "I" rather than "we",
 * concrete numbers rather than adjectives, and the constraints stated plainly
 * instead of being left for the reader to discover.
 */

import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { useDocumentTitle } from "@/lib/useDocumentTitle"

export function AboutPage() {
  const { t } = useTranslation()
  useDocumentTitle(t("about.title"))

  return (
    <article className="max-w-(--container-narrow) mx-auto px-6 lg:px-12 py-16 lg:py-24">
      <header>
        <h1
          className="font-serif text-ink mb-6"
          style={{ fontSize: "clamp(34px, 4.5vw, 52px)", lineHeight: 1.1, fontWeight: 700, letterSpacing: "-0.02em" }}
        >
          {t("about.title")}
        </h1>
        <p className="text-body text-ink-2" style={{ fontSize: "20px", lineHeight: "34px" }}>
          {t("about.lead")}
        </p>
      </header>

      <hr className="border-rule my-12" />

      <Section title={t("about.whoTitle")}>
        <P>{t("about.whoBody")}</P>
      </Section>

      <hr className="border-rule my-12" />

      <Section title={t("about.whyTitle")}>
        <P>{t("about.whyBody1")}</P>
        <P className="mt-4">{t("about.whyBody2")}</P>
      </Section>

      <hr className="border-rule my-12" />

      <Section title={t("about.moneyTitle")}>
        <P>{t("about.moneyBody")}</P>
      </Section>

      <hr className="border-rule my-12" />

      <Section title={t("about.limitsTitle")}>
        <P>{t("about.limitsBody")}</P>
        <ul
          className="mt-6 space-y-3 list-disc list-inside text-body text-ink-2 font-sans"
          style={{ fontSize: "17px", lineHeight: "28px" }}
        >
          <li>{t("about.limit1")}</li>
          <li>{t("about.limit2")}</li>
          <li>{t("about.limit3")}</li>
        </ul>
      </Section>

      <hr className="border-rule my-12" />

      <Section title={t("about.errorTitle")}>
        <P>{t("about.errorBody")}</P>
        <p className="mt-6">
          <a
            href="mailto:hello@trustgive.org"
            className="text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            hello@trustgive.org
          </a>
        </p>
      </Section>

      <hr className="border-rule my-12" />

      <Section title={t("about.openTitle")}>
        <P>{t("about.openBody")}</P>
        <p className="mt-6 flex flex-wrap gap-x-6 gap-y-2">
          <a
            href="https://github.com/AlexOpasnost/trustgive"
            target="_blank"
            rel="noopener noreferrer me"
            className="text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("about.linkCode")}
          </a>
          <Link
            to="/methodology"
            className="text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("about.linkMethodology")}
          </Link>
          <a
            href="https://api.trustgive.org/api/docs/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("about.linkApi")}
          </a>
        </p>
      </Section>
    </article>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">{title}</h2>
      {children}
    </section>
  )
}

function P({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <p
      className={`text-body leading-relaxed text-ink-2 ${className}`}
      style={{ fontSize: "19px", lineHeight: "32px" }}
    >
      {children}
    </p>
  )
}
