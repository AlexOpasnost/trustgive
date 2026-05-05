import { HugeiconsIcon } from "@hugeicons/react"
import { Tick02Icon, Search01Icon, Menu01Icon } from "@hugeicons/core-free-icons"
import { useTranslation } from "react-i18next"
import { Link, NavLink } from "react-router-dom"

import { cn } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"

export function TopNav() {
  const { t, i18n } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const setLang = usePreferences((s) => s.setLang)

  const switchLang = (newLang: "en" | "ru") => {
    setLang(newLang)
    void i18n.changeLanguage(newLang)
  }

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    cn(
      "text-body-sm font-medium px-2 py-1 transition-colors",
      isActive ? "text-ink border-b-2 border-verified" : "text-ink-3 hover:text-ink"
    )

  return (
    <header className="sticky top-0 z-30 bg-paper/95 backdrop-blur border-b border-rule">
      <div className="max-w-(--container-default) mx-auto px-6 lg:px-12 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-semibold text-h4">
          <HugeiconsIcon icon={Tick02Icon} size={20} className="text-verified" />
          <span>TrustGive</span>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          <NavLink to="/charities" className={navLinkClass}>
            {t("nav.catalog")}
          </NavLink>
          <NavLink to="/methodology" className={navLinkClass}>
            {t("nav.methodology")}
          </NavLink>
        </nav>

        <div className="flex items-center gap-3">
          <button
            type="button"
            className="hidden md:inline-flex items-center gap-2 px-3 py-1 text-caption text-ink-3 border border-rule rounded-md hover:text-ink"
            aria-label={t("nav.search")}
          >
            <HugeiconsIcon icon={Search01Icon} size={14} />
            <span className="font-mono">⌘K</span>
          </button>
          <div className="flex items-center text-body-sm" role="group" aria-label="Language">
            <button
              type="button"
              onClick={() => switchLang("en")}
              className={cn("px-2 py-1", lang === "en" ? "text-ink font-medium" : "text-ink-3")}
              aria-pressed={lang === "en"}
            >
              EN
            </button>
            <span className="text-ink-3">·</span>
            <button
              type="button"
              onClick={() => switchLang("ru")}
              className={cn("px-2 py-1", lang === "ru" ? "text-ink font-medium" : "text-ink-3")}
              aria-pressed={lang === "ru"}
              aria-label={t("nav.switchLang")}
            >
              RU
            </button>
          </div>
          <button type="button" className="md:hidden" aria-label="Open menu">
            <HugeiconsIcon icon={Menu01Icon} size={24} />
          </button>
        </div>
      </div>
    </header>
  )
}
