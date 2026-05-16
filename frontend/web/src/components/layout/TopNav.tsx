/**
 * TopNav — DESIGN.md v3.0 §G.
 *
 * v3.0 changes:
 *   - ⌘K command-palette button REMOVED (entire palette deleted).
 *   - Compare link REMOVED (page deleted).
 *   - Lang toggle: clicking RU/EN updates Zustand prefs + i18next.
 */
import { HugeiconsIcon } from "@hugeicons/react"
import { Menu01Icon } from "@hugeicons/core-free-icons"
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
      <div className="max-w-(--container-wide) mx-auto px-6 lg:px-12 h-16 flex items-center justify-between">
        {/*
          Brand wordmark. Dagger (†) = academic citation mark — specific to
          what TrustGive does: cite the source filing instead of grading.
          Wordmark in Source Serif Bold, dagger in forest-green verified
          accent. No icon library — these are the brand.
        */}
        <Link to="/" className="flex items-baseline gap-1.5" aria-label="TrustGive">
          <span
            className="font-serif text-verified"
            style={{ fontSize: "26px", lineHeight: "1", fontWeight: 700 }}
            aria-hidden="true"
          >
            †
          </span>
          <span
            className="font-serif text-ink"
            style={{ fontSize: "22px", lineHeight: "1", fontWeight: 700, letterSpacing: "-0.01em" }}
          >
            TrustGive
          </span>
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
