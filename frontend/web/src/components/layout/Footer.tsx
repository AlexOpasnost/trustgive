/**
 * Footer — DESIGN_v4.md §5 (chrome).
 *
 * v4: paper-v4 background (not a separate surface), no green checkmark in
 * the wordmark, hairline rules using rule-v4. Column heads in Inter caps,
 * links in Inter ui-md, colophon in Geist Mono. Wordmark in Source Serif
 * at display-md scale — same family as the page, not a banner.
 */
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

export function Footer() {
  const { t } = useTranslation()
  const year = new Date().getFullYear()

  return (
    <footer
      style={{
        background: "var(--color-paper-v4)",
        borderTop: "1px solid var(--color-rule-v4)",
      }}
    >
      <div className="max-w-[1280px] mx-auto px-6 lg:px-12 pt-16 pb-10">
        {/* Wordmark + tagline */}
        <div
          className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 pb-10 mb-10"
          style={{ borderBottom: "1px solid var(--color-rule-v4)" }}
        >
          <span
            className="font-serif"
            style={{
              fontSize: "44px",
              lineHeight: 1,
              fontWeight: 400,
              letterSpacing: "-0.02em",
              color: "var(--color-ink-v4)",
            }}
          >
            TrustGive
          </span>
          <p
            className="font-serif italic max-w-md md:text-right"
            style={{
              fontSize: "var(--text-body-v4)",
              lineHeight: "var(--text-body-v4--line-height)",
              color: "var(--color-ink-2-v4)",
            }}
          >
            {t("footer.tagline")}
          </p>
        </div>

        {/* 3-column nav */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-y-10 gap-x-8 mb-12">
          <FooterCol title={t("footer.discover.title")}>
            <FooterLink to="/charities">{t("footer.discover.catalog")}</FooterLink>
            <FooterLink to="/charities?country=US">{t("footer.discover.us")}</FooterLink>
            <FooterLink to="/charities?country=GB">{t("footer.discover.uk")}</FooterLink>
            <FooterLink to="/charities?country=RU">{t("footer.discover.ru")}</FooterLink>
          </FooterCol>

          <FooterCol title={t("footer.method.title")}>
            <FooterLink to="/methodology">{t("footer.method.howWeVerify")}</FooterLink>
            <FooterLink to="/methodology#sources">{t("footer.method.dataSources")}</FooterLink>
            <FooterLink to="/methodology#standards">{t("footer.method.standards")}</FooterLink>
          </FooterCol>

          <FooterCol title={t("footer.about.title")}>
            <FooterExternalLink href="https://github.com/AlexOpasnost/trustgive">
              {t("footer.about.github")}
            </FooterExternalLink>
            <FooterExternalLink href="https://github.com/AlexOpasnost/trustgive/blob/main/CHANGELOG.md">
              {t("footer.about.changelog")}
            </FooterExternalLink>
            <FooterExternalLink href="mailto:hello@trustgive.org">
              {t("footer.about.contact")}
            </FooterExternalLink>
          </FooterCol>
        </div>

        {/* Bottom colophon */}
        <div
          className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pt-6 font-mono"
          style={{
            borderTop: "1px solid var(--color-rule-v4)",
            fontSize: "var(--text-mono-sm)",
            color: "var(--color-ink-3-v4)",
          }}
        >
          <p>© {year} TrustGive · {t("footer.colophon")}</p>
          <p>
            {t("footer.builtWith")}{" "}
            <span style={{ color: "var(--color-ink-2-v4)" }}>
              Source Serif 4 · Inter · Geist Mono
            </span>
          </p>
        </div>
      </div>
    </footer>
  )
}

function FooterCol({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3
        className="font-sans uppercase mb-4"
        style={{
          fontSize: "var(--text-ui-sm)",
          letterSpacing: "0.16em",
          color: "var(--color-ink-3-v4)",
          fontWeight: 500,
        }}
      >
        {title}
      </h3>
      <ul className="space-y-3">{children}</ul>
    </div>
  )
}

function FooterLink({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <li>
      <Link
        to={to}
        className="font-sans transition-colors duration-150"
        style={{
          fontSize: "var(--text-ui-md)",
          color: "var(--color-ink-2-v4)",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.color = "var(--color-ink-v4)")}
        onMouseLeave={(e) => (e.currentTarget.style.color = "var(--color-ink-2-v4)")}
      >
        {children}
      </Link>
    </li>
  )
}

function FooterExternalLink({ href, children }: { href: string; children: React.ReactNode }) {
  const isExternal = href.startsWith("http")
  return (
    <li>
      <a
        href={href}
        target={isExternal ? "_blank" : undefined}
        rel={isExternal ? "noopener noreferrer" : undefined}
        className="font-sans transition-colors duration-150"
        style={{
          fontSize: "var(--text-ui-md)",
          color: "var(--color-ink-2-v4)",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.color = "var(--color-ink-v4)")}
        onMouseLeave={(e) => (e.currentTarget.style.color = "var(--color-ink-2-v4)")}
      >
        {children}
      </a>
    </li>
  )
}
