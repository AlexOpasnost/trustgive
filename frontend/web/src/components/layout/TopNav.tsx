/**
 * TopNav — DESIGN_v4.md §5 (chrome).
 *
 * v4 chrome rules: minimum weight. Thin top bar, no sticky-blur, no green
 * accent on the brand mark, nav links as Inter ui-md with the active route
 * underlined (not a green bottom-border). Lang toggle simplified to two
 * Inter ui-sm buttons separated by a middot.
 *
 * The header is intentionally NOT sticky in v4. Editorial sites tend to let
 * the masthead scroll off; sticky chrome competes with the lead headline.
 */
import { HugeiconsIcon } from "@hugeicons/react"
import { Menu01Icon } from "@hugeicons/core-free-icons"
import { useTranslation } from "react-i18next"
import { Link, NavLink } from "react-router-dom"

import { usePreferences } from "@/store/preferences"

export function TopNav() {
  const { t, i18n } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const setLang = usePreferences((s) => s.setLang)

  const switchLang = (newLang: "en" | "ru") => {
    setLang(newLang)
    void i18n.changeLanguage(newLang)
  }

  return (
    <header
      style={{
        background: "var(--color-paper-v4)",
        borderBottom: "1px solid var(--color-rule-v4)",
      }}
    >
      <div className="max-w-[1280px] mx-auto px-6 lg:px-12 h-14 flex items-center justify-between">
        {/* Wordmark — Source Serif at a confident-but-modest size. The check-
            mark icon and verified-green tint from v3 are gone. */}
        <Link
          to="/"
          className="font-serif"
          style={{
            fontSize: "22px",
            lineHeight: 1,
            fontWeight: 600,
            letterSpacing: "-0.01em",
            color: "var(--color-ink-v4)",
          }}
        >
          TrustGive
        </Link>

        {/* Centre nav — Inter 15px, active route underlined */}
        <nav className="hidden md:flex items-center gap-8">
          <NavLink
            to="/charities"
            className="font-sans"
            style={({ isActive }) => ({
              fontSize: "var(--text-ui-md)",
              color: isActive ? "var(--color-ink-v4)" : "var(--color-ink-3-v4)",
              fontWeight: 500,
              textDecoration: isActive ? "underline" : "none",
              textDecorationThickness: "1px",
              textUnderlineOffset: "6px",
            })}
          >
            {t("nav.catalog")}
          </NavLink>
          <NavLink
            to="/methodology"
            className="font-sans"
            style={({ isActive }) => ({
              fontSize: "var(--text-ui-md)",
              color: isActive ? "var(--color-ink-v4)" : "var(--color-ink-3-v4)",
              fontWeight: 500,
              textDecoration: isActive ? "underline" : "none",
              textDecorationThickness: "1px",
              textUnderlineOffset: "6px",
            })}
          >
            {t("nav.methodology")}
          </NavLink>
        </nav>

        {/* Right side — lang toggle + mobile menu */}
        <div className="flex items-center gap-4">
          <div
            className="flex items-center"
            role="group"
            aria-label="Language"
            style={{ fontSize: "var(--text-ui-sm)" }}
          >
            <button
              type="button"
              onClick={() => switchLang("en")}
              className="font-sans px-1"
              style={{
                color:
                  lang === "en" ? "var(--color-ink-v4)" : "var(--color-ink-3-v4)",
                fontWeight: lang === "en" ? 600 : 500,
              }}
              aria-pressed={lang === "en"}
            >
              EN
            </button>
            <span
              className="mx-1"
              style={{ color: "var(--color-ink-3-v4)" }}
              aria-hidden="true"
            >
              ·
            </span>
            <button
              type="button"
              onClick={() => switchLang("ru")}
              className="font-sans px-1"
              style={{
                color:
                  lang === "ru" ? "var(--color-ink-v4)" : "var(--color-ink-3-v4)",
                fontWeight: lang === "ru" ? 600 : 500,
              }}
              aria-pressed={lang === "ru"}
              aria-label={t("nav.switchLang")}
            >
              RU
            </button>
          </div>
          <button
            type="button"
            className="md:hidden"
            aria-label="Open menu"
            style={{ color: "var(--color-ink-v4)" }}
          >
            <HugeiconsIcon icon={Menu01Icon} size={22} />
          </button>
        </div>
      </div>
    </header>
  )
}
