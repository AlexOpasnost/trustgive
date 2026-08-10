import { clsx, type ClassValue } from "clsx"
import { extendTailwindMerge } from "tailwind-merge"

/**
 * The project's own type scale and palette, declared to tailwind-merge.
 *
 * Without this, `cn()` silently deletes class names. tailwind-merge resolves
 * conflicts by putting every class in a group, and it only knows the groups for
 * *stock* Tailwind names — `text-accent-on` and `text-prose` mean nothing to it,
 * so it guessed, decided they collided with `text-body`, and dropped whichever
 * came first.
 *
 * That was live. The primary Button composes `bg-verified text-verified-on` with
 * a size variant carrying `text-body`, so the button's text colour was being
 * merged away and the label had been rendering in inherited ink on the green
 * fill — about 3.4:1, under the AA floor, on the donate button. It only became
 * visible when the fill moved to ink and the label went ink-on-ink.
 *
 * Splitting the names into the right two groups is the fix: sizes conflict with
 * sizes, colours conflict with colours, and neither touches the other. Anything
 * added to `@theme` in index.css has to be added here too — `cn()` cannot infer
 * it, and the failure mode is silent.
 */
const TEXT_SIZES = [
  // Editorial scale
  "display",
  "section",
  "banner",
  "lead",
  "prose",
  "prose-sm",
  // UI scale
  "h1",
  "h2",
  "h3",
  "h4",
  "body",
  "body-sm",
  "caption",
  // Brand
  "wordmark",
  "wordmark-lg",
]

const COLORS = [
  "paper",
  "surface",
  "surface-raised",
  "ink",
  "ink-2",
  "ink-3",
  "rule",
  "clay",
  "accent",
  "accent-on",
  "verified",
  "verified-on",
  "verified-soft",
  "verified-fixed",
  "ink-fixed",
  "warning",
  "warning-soft",
  "error",
  "error-soft",
  "info",
  "info-soft",
]

const twMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      "font-size": [{ text: TEXT_SIZES }],
      "text-color": [{ text: COLORS }],
      "bg-color": [{ bg: COLORS }],
      "border-color": [{ border: COLORS }],
    },
  },
})

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatUsd(value: number | string | null | undefined, options: { compact?: boolean } = {}): string {
  if (value == null) return "—"
  const num = typeof value === "string" ? Number(value) : value
  if (Number.isNaN(num)) return "—"
  if (options.compact) {
    return new Intl.NumberFormat("en-US", {
      notation: "compact",
      maximumFractionDigits: 1,
      style: "currency",
      currency: "USD",
    }).format(num)
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(num)
}

/**
 * Render an ISO date (`2023-12-31`) as a readable one ("31 December 2023").
 *
 * Dates on this site are always facts taken from a filing, so an unparseable or
 * absent value returns null rather than a placeholder — the caller drops the
 * clause instead of printing "—" where a regulator's date should be.
 */
export function formatIsoDate(
  value: string | null | undefined,
  lang: "en" | "ru" = "en",
): string | null {
  if (!value) return null
  const parsed = new Date(`${value.slice(0, 10)}T00:00:00Z`)
  if (Number.isNaN(parsed.getTime())) return null
  const formatted = new Intl.DateTimeFormat(lang === "ru" ? "ru-RU" : "en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(parsed)
  // `ru-RU` appends the era marker " г." — "2 августа 2026 г.". That trailing
  // period collides with the sentence punctuation in the locale strings, which
  // produced "Каталог перепроверен 2 августа 2026 г.." on the homepage. Strip it
  // here so punctuation stays the sentence's business, in one place, rather than
  // every Russian string having to know how the formatter ends.
  return formatted.replace(/\s*г\.$/, "")
}

export function formatPercent(value: number | string | null | undefined): string {
  if (value == null) return "—"
  const num = typeof value === "string" ? Number(value) : value
  if (Number.isNaN(num)) return "—"
  return `${num.toFixed(1)}%`
}
