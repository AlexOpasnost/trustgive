import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

export function Footer() {
  const { t } = useTranslation()
  return (
    <footer className="border-t border-rule mt-16">
      <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 py-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <p className="text-body-sm text-ink-2">
          <span className="font-semibold text-ink">TrustGive</span> · {t("footer.tagline")}
        </p>
        <nav className="flex items-center gap-4 text-body-sm text-ink-3">
          <Link to="/methodology" className="hover:text-ink">
            {t("footer.links.methodology")}
          </Link>
          <a href="https://github.com/AlexOpasnost/trustgive" target="_blank" rel="noopener noreferrer" className="hover:text-ink">
            {t("footer.links.github")}
          </a>
          <a href="/api/feed.rss" className="hover:text-ink">
            {t("footer.links.rss")}
          </a>
        </nav>
      </div>
    </footer>
  )
}
