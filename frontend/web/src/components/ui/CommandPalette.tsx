/**
 * ⌘K command palette — Linear/Stripe-style search.
 *
 * Triggered via Cmd+K (macOS) / Ctrl+K (Windows/Linux), or click on the
 * pill in TopNav. Uses `cmdk` for the keyboard-navigation primitive.
 *
 * Search debounces against /api/charities/?q= — no autocomplete service.
 */
import { Command } from "cmdk"
import { HugeiconsIcon } from "@hugeicons/react"
import {
  ArrowRight01Icon,
  Building03Icon,
  FileVerifiedIcon,
  Search01Icon,
  Tick02Icon,
} from "@hugeicons/core-free-icons"
import { useEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

import { api } from "@/lib/api"
import { track } from "@/lib/posthog"
import type { CharitySummary } from "@/types/api"

type Props = {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function CommandPalette({ open, onOpenChange }: Props) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<CharitySummary[]>([])
  const [loading, setLoading] = useState(false)
  const debounceRef = useRef<number | null>(null)

  // Reset on close
  useEffect(() => {
    if (!open) {
      setQuery("")
      setResults([])
    }
  }, [open])

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) window.clearTimeout(debounceRef.current)
    if (!query.trim() || query.trim().length < 2) {
      setResults([])
      return
    }
    setLoading(true)
    debounceRef.current = window.setTimeout(async () => {
      try {
        const data = await api.listCharities({ q: query, page_size: 8 })
        setResults(data.results)
      } catch {
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 220)
    return () => {
      if (debounceRef.current) window.clearTimeout(debounceRef.current)
    }
  }, [query])

  const goto = (path: string, telemetry: string) => {
    track(telemetry, { from: "cmdk", path })
    navigate(path)
    onOpenChange(false)
  }

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] bg-paper/70 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onOpenChange(false)}
      role="presentation"
    >
      <Command
        label={t("nav.search")}
        loop
        className="w-[min(640px,calc(100vw-2rem))] bg-surface-raised border border-rule rounded-md shadow-none overflow-hidden"
      >
        <div className="flex items-center gap-3 px-5 py-4 border-b border-rule">
          <HugeiconsIcon icon={Search01Icon} size={18} className="text-ink-3 shrink-0" />
          <Command.Input
            value={query}
            onValueChange={setQuery}
            placeholder={t("search.placeholder")}
            className="flex-1 bg-transparent outline-none text-body text-ink placeholder:text-ink-3"
            autoFocus
          />
          <kbd className="font-mono text-caption text-ink-3 border border-rule rounded-sm px-1.5 py-0.5">
            ESC
          </kbd>
        </div>

        <Command.List className="max-h-[60vh] overflow-y-auto py-2">
          {loading && (
            <div className="px-5 py-4 text-body-sm text-ink-3">{t("common.loading")}</div>
          )}

          {!loading && query.trim().length >= 2 && results.length === 0 && (
            <Command.Empty className="px-5 py-6 text-body-sm text-ink-3">
              {t("search.noResults", { q: query })}
            </Command.Empty>
          )}

          {results.length > 0 && (
            <Command.Group heading={t("search.charities")}>
              {results.map((c) => (
                <Command.Item
                  key={c.slug}
                  value={`${c.slug} ${c.name?.en} ${c.name?.ru} ${c.registration_id}`}
                  onSelect={() => goto(`/charities/${c.slug}`, "cmdk_navigate_charity")}
                  className="flex items-center gap-3 px-5 py-3 cursor-pointer aria-selected:bg-paper"
                >
                  <HugeiconsIcon icon={Building03Icon} size={16} className="text-ink-3 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-body text-ink truncate">{c.name?.en || c.slug}</div>
                    <div className="text-caption text-ink-3 font-mono">
                      {c.country} · {c.registration_id}
                    </div>
                  </div>
                  {c.verification_status === "verified" && (
                    <HugeiconsIcon icon={Tick02Icon} size={14} className="text-verified shrink-0" />
                  )}
                </Command.Item>
              ))}
            </Command.Group>
          )}

          <Command.Group heading={t("search.quickNav")}>
            <PaletteAction
              icon={Building03Icon}
              label={t("search.allCharities")}
              onSelect={() => goto("/charities", "cmdk_navigate_catalog")}
            />
            <PaletteAction
              icon={FileVerifiedIcon}
              label={t("search.methodology")}
              onSelect={() => goto("/methodology", "cmdk_navigate_methodology")}
            />
            <PaletteAction
              icon={Building03Icon}
              label={t("search.usCharities")}
              onSelect={() => goto("/charities?country=US", "cmdk_navigate_us")}
            />
            <PaletteAction
              icon={Building03Icon}
              label={t("search.ukCharities")}
              onSelect={() => goto("/charities?country=GB", "cmdk_navigate_uk")}
            />
            <PaletteAction
              icon={Building03Icon}
              label={t("search.ruCharities")}
              onSelect={() => goto("/charities?country=RU", "cmdk_navigate_ru")}
            />
          </Command.Group>
        </Command.List>

        <div className="flex items-center justify-between px-5 py-3 border-t border-rule text-caption text-ink-3 font-mono">
          <span>↑↓ navigate · ↵ open · esc close</span>
          <span>{t("search.poweredBy")}</span>
        </div>
      </Command>
    </div>
  )
}

function PaletteAction({
  icon,
  label,
  onSelect,
}: {
  icon: typeof Search01Icon
  label: string
  onSelect: () => void
}) {
  return (
    <Command.Item
      value={label}
      onSelect={onSelect}
      className="flex items-center gap-3 px-5 py-3 cursor-pointer aria-selected:bg-paper"
    >
      <HugeiconsIcon icon={icon} size={16} className="text-ink-3 shrink-0" />
      <span className="flex-1 text-body text-ink">{label}</span>
      <HugeiconsIcon icon={ArrowRight01Icon} size={14} className="text-ink-3" />
    </Command.Item>
  )
}
