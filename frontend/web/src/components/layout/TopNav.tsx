/**
 * TopNav — DESIGN.md v3.0 §G.
 *
 * v3.0 changes:
 *   - ⌘K command-palette button REMOVED (entire palette deleted).
 *   - Compare link REMOVED (page deleted).
 *   - Lang toggle: clicking RU/EN updates Zustand prefs + i18next.
 */
import { HugeiconsIcon } from "@hugeicons/react"
import { Menu01Icon, Moon02Icon, Sun03Icon } from "@hugeicons/core-free-icons"
import { useSyncExternalStore } from "react"
import { useTranslation } from "react-i18next"
import { Link, NavLink } from "react-router-dom"

import { SearchBox } from "@/components/search/SearchBox"

import { resolveScheme } from "@/lib/colorScheme"
import { cn } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"

/**
 * What the reader is actually looking at right now.
 *
 * The stored preference is one of three values, but the button offers one
 * choice — "give me the other one" — so it has to know which of light and dark
 * is on screen. Under "system" that answer comes from the OS and can change
 * while the page is open, so the media query is subscribed to rather than read.
 */
function useActiveScheme(): "light" | "dark" {
  const preference = usePreferences((s) => s.colorScheme)
  const systemIsDark = useSyncExternalStore(
    (onChange) => {
      if (typeof window === "undefined" || !window.matchMedia) return () => {}
      const query = window.matchMedia("(prefers-color-scheme: dark)")
      query.addEventListener("change", onChange)
      return () => query.removeEventListener("change", onChange)
    },
    () => typeof window !== "undefined" && window.matchMedia?.("(prefers-color-scheme: dark)").matches,
    () => false
  )
  if (preference === "system") return systemIsDark ? "dark" : "light"
  return resolveScheme(preference)
}

export function TopNav() {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  // Setting the store is the whole switch: lib/i18n subscribes and moves
  // i18next with it. Calling changeLanguage here too would restore the
  // two-writers arrangement that made the language not survive a reload.
  const switchLang = usePreferences((s) => s.setLang)
  const setColorScheme = usePreferences((s) => s.setColorScheme)
  const activeScheme = useActiveScheme()

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    cn(
      "text-body-sm font-medium px-2 py-1 transition-colors",
      // Accent, not verified green: an underline marks which page you are on.
      isActive ? "text-ink border-b-2 border-accent" : "text-ink-3 hover:text-ink"
    )

  return (
    <header className="sticky top-0 z-30 bg-paper/95 backdrop-blur border-b border-rule">
      <div className="max-w-(--container-wide) mx-auto px-6 lg:px-12 h-16 flex items-center justify-between">
        {/*
          Wordmark only. It used to be preceded by a dagger (†) in verified
          green — chosen as the academic citation mark, which is exactly what
          this project does. The joke was good and the glyph was wrong: at
          wordmark size it reads as a Christian cross, which a secular global
          charity catalogue should not be wearing, and in a list it reads as the
          "deceased" marker. Two misreadings are more than one pun is worth.

          The green went with it. That colour now means one thing — a regulator
          confirmed this record — and a logo is not a verification claim.
        */}
        <Link to="/" className="flex items-baseline" aria-label="TrustGive">
          <span className="font-serif text-wordmark font-bold text-ink">TrustGive</span>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          <NavLink to="/charities" className={navLinkClass}>
            {t("nav.catalog")}
          </NavLink>
          <NavLink to="/research" className={navLinkClass}>
            {t("nav.research")}
          </NavLink>
          <NavLink to="/methodology" className={navLinkClass}>
            {t("nav.methodology")}
          </NavLink>
          <NavLink to="/about" className={navLinkClass}>
            {t("nav.about")}
          </NavLink>
          {/* Persistent, because the arrival is usually a name rather than a
              browse intent. Hidden below md — the mobile header has no room,
              and the catalogue carries its own field. */}
          <div className="hidden md:block ml-2">
            <SearchBox variant="compact" />
          </div>
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
          {/* One button, one choice: give me the other one. The stored
              preference has three values, but a three-way cycle behind a single
              icon is a puzzle, and "system" is the default a reader never has to
              think about — it only stops applying once they disagree with it. */}
          <button
            type="button"
            onClick={() => setColorScheme(activeScheme === "dark" ? "light" : "dark")}
            className="p-1 text-ink-3 hover:text-ink transition-colors"
            aria-label={t(activeScheme === "dark" ? "nav.themeLight" : "nav.themeDark")}
            title={t(activeScheme === "dark" ? "nav.themeLight" : "nav.themeDark")}
          >
            <HugeiconsIcon
              icon={activeScheme === "dark" ? Sun03Icon : Moon02Icon}
              size={18}
              aria-hidden="true"
            />
          </button>
          <button type="button" className="md:hidden" aria-label="Open menu">
            <HugeiconsIcon icon={Menu01Icon} size={24} />
          </button>
        </div>
      </div>
    </header>
  )
}
