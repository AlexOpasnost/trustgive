/**
 * Footer — DESIGN.md v3.0 §J.
 *
 * v3.0 changes:
 *   - Compare link REMOVED from Discover column.
 *   - Open Data column REMOVED entirely (per Frontend agent task spec).
 *   - 4-col → 3-col grid (Discover / Methodology / About).
 */
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

export function Footer() {
  const { t } = useTranslation()
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-rule bg-surface">
      <div className="max-w-(--container-wide) mx-auto px-6 lg:px-12 pt-20 pb-12">
        {/* Wordmark + tagline row */}
        <div className="flex items-end justify-between gap-8 mb-16 pb-12 border-b border-rule">
          <div className="flex items-baseline gap-3">
            {/* Dagger citation mark — see TopNav for rationale. */}
            <span
              className="font-serif text-verified"
              style={{ fontSize: "52px", lineHeight: "1", fontWeight: 700 }}
              aria-hidden="true"
            >
              †
            </span>
            <span
              className="font-serif text-ink"
              style={{ fontSize: "44px", lineHeight: 1, fontWeight: 700, letterSpacing: "-0.02em" }}
            >
              TrustGive
            </span>
          </div>
          <p className="text-body-sm text-ink-2 max-w-md text-right hidden md:block">
            {t("footer.tagline")}
          </p>
        </div>

        {/* 3-column nav (v3.0: dropped Open Data column) */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-y-12 gap-x-8 mb-16">
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

        {/* Bottom row — colophon */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pt-8 border-t border-rule text-caption text-ink-3 font-mono">
          <p>
            © {year} TrustGive · {t("footer.colophon")}
          </p>
          <p>
            {t("footer.builtWith")}{" "}
            <span className="text-ink-2">Inter · Source Serif 4 · Geist Mono · Hugeicons</span>
          </p>
        </div>
      </div>
    </footer>
  )
}

function FooterCol({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-caption uppercase tracking-widest text-ink-3 font-medium mb-4">{title}</h3>
      <ul className="space-y-3">{children}</ul>
    </div>
  )
}

function FooterLink({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <li>
      <Link to={to} className="text-body text-ink-2 hover:text-ink transition-colors">
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
        className="text-body text-ink-2 hover:text-ink transition-colors"
      >
        {children}
      </a>
    </li>
  )
}
