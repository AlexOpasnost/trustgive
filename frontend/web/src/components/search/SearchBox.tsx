/**
 * SearchBox — find a named charity.
 *
 * The most common way someone arrives here is with a name in hand: a friend
 * mentioned an organisation, an email asked for money, a link looked plausible.
 * Until now the only way in was the catalogue's cause and region filters, which
 * answer a different question entirely.
 *
 * Submitting navigates to /charities?q=… rather than opening a dropdown of
 * predictions. That keeps the result addressable — the URL can be shared, cited
 * and indexed — and it means an empty result is a real page that can explain
 * itself, which matters now that a missing charity means "not verified" rather
 * than "does not exist".
 */

import { Search01Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useState, type FormEvent } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

type Props = {
  /** `hero` is the large homepage field; `compact` sits in the header. */
  variant?: "hero" | "compact"
  autoFocus?: boolean
}

export function SearchBox({ variant = "hero", autoFocus = false }: Props) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [value, setValue] = useState("")

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    const q = value.trim()
    if (!q) return
    navigate(`/charities?q=${encodeURIComponent(q)}`)
  }

  const isHero = variant === "hero"

  return (
    <form
      onSubmit={onSubmit}
      role="search"
      className={isHero ? "w-full max-w-[560px]" : "w-full max-w-[240px]"}
    >
      <label htmlFor={`search-${variant}`} className="sr-only">
        {t("search.label")}
      </label>
      <div
        className={`
          flex items-center gap-2 bg-surface-raised border border-rule rounded-md
          focus-within:border-ink transition-colors
          ${isHero ? "px-4 py-3" : "px-3 py-1.5"}
        `}
      >
        <HugeiconsIcon
          icon={Search01Icon}
          size={isHero ? 18 : 15}
          aria-hidden="true"
          className="text-ink-3 shrink-0"
        />
        <input
          id={`search-${variant}`}
          type="search"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={t("search.placeholder")}
          autoFocus={autoFocus}
          autoComplete="off"
          className={`
            flex-1 min-w-0 bg-transparent text-ink placeholder:text-ink-3
            focus:outline-none
            ${isHero ? "text-body" : "text-body-sm"}
          `}
        />
        {isHero && (
          <button
            type="submit"
            className="shrink-0 bg-ink text-paper rounded-sm px-4 py-1.5 text-body-sm font-medium hover:opacity-90"
          >
            {t("search.submit")}
          </button>
        )}
      </div>
    </form>
  )
}
