import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

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
