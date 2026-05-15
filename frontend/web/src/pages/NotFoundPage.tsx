import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { useDocumentTitle } from "@/lib/useDocumentTitle"

export function NotFoundPage() {
  const { t } = useTranslation()
  useDocumentTitle(t("common.notFound"))
  return (
    <main
      style={{ background: "var(--color-paper-v4)", color: "var(--color-ink-v4)" }}
      className="px-6 lg:px-12 max-w-[640px] mx-auto py-24 lg:py-32 text-center"
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
        404
      </p>
      <h1
        className="font-serif mb-8"
        style={{
          fontSize: "clamp(40px, 6vw, 64px)",
          lineHeight: 1.05,
          fontWeight: 400,
          letterSpacing: "-0.015em",
          color: "var(--color-ink-v4)",
        }}
      >
        {t("common.notFound")}
      </h1>
      <Link
        to="/charities"
        className="font-sans inline-flex items-baseline gap-2 group"
        style={{
          fontSize: "var(--text-ui-md)",
          color: "var(--color-link)",
          fontWeight: 500,
        }}
      >
        <span className="underline decoration-1 underline-offset-4 group-hover:no-underline">
          {t("detail.v4.backToArchive")}
        </span>
        <span aria-hidden="true">→</span>
      </Link>
    </main>
  )
}
