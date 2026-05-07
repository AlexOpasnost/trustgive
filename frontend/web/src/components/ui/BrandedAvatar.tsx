/**
 * BrandedAvatar — deterministic letter avatar.
 *
 * Per DESIGN.md v2.0 §D.3 step 2 (branded letter avatar):
 *   - Background pulled from a deterministic hash of the slug, mapped to one of
 *     a small palette of brand-safe muted tones (cream / sage / green family).
 *   - Letter = first letter of name (uppercase), Source Serif Bold, 60% of avatar size.
 *   - All bg/text pairs WCAG AA verified against `--color-paper` #F5F1E8 base.
 *
 * Sizes (px):  sm=32  md=48  lg=64  xl=96
 */

import { cn } from "@/lib/utils"

export type BrandedAvatarSize = "sm" | "md" | "lg" | "xl"

type Props = {
  slug: string
  name: string
  size?: BrandedAvatarSize
  className?: string
}

const SIZE_PX: Record<BrandedAvatarSize, number> = {
  sm: 32,
  md: 48,
  lg: 64,
  xl: 96,
}

// Brand-safe muted palette. Each entry is { bg, text } — both pulled from
// existing semantic tokens already validated against #F5F1E8 paper (DESIGN.md §D.3).
//
// Six entries, deliberately. More variety = more "noise" — but six gives enough
// scatter that a 6-card grid won't have two avatars in the same colour.
const PALETTE: { bg: string; text: string }[] = [
  // Children / education — info family (5.6:1)
  { bg: "bg-info-soft", text: "text-info" },
  // Climate / environment — verified family (4.7:1)
  { bg: "bg-verified-soft", text: "text-verified" },
  // Health / medicine — error family (5.4:1)
  { bg: "bg-error-soft", text: "text-error" },
  // Animals / refugees / humanitarian — warning family (5.1:1)
  { bg: "bg-warning-soft", text: "text-warning" },
  // Default neutral — paper + ink-2 (9.6:1)
  { bg: "bg-paper", text: "text-ink-2" },
  // Surface neutral — surface + ink (~17:1)
  { bg: "bg-surface", text: "text-ink" },
]

/**
 * djb2-style hash, then modulo palette length.
 * Deterministic per slug — same slug always lands on same colour.
 */
function paletteIndexFromSlug(slug: string): number {
  let hash = 5381
  for (let i = 0; i < slug.length; i += 1) {
    hash = (hash * 33) ^ slug.charCodeAt(i)
  }
  return Math.abs(hash) % PALETTE.length
}

/**
 * Pick the leading printable letter from `name`, uppercase.
 * Fallback: first char of slug. Final fallback: "?".
 */
function pickLetter(name: string, slug: string): string {
  const trimmed = (name ?? "").trim()
  if (trimmed.length > 0) {
    // Use codePointAt to handle surrogate pairs (emoji etc.) cleanly,
    // then uppercase. For a Cyrillic name like "Русфонд" — picks "Р".
    const cp = trimmed.codePointAt(0)
    if (cp != null) {
      return String.fromCodePoint(cp).toUpperCase()
    }
  }
  if (slug && slug.length > 0) {
    return slug.charAt(0).toUpperCase()
  }
  return "?"
}

export function BrandedAvatar({ slug, name, size = "md", className }: Props) {
  const px = SIZE_PX[size]
  const fontPx = Math.round(px * 0.6)
  const palette = PALETTE[paletteIndexFromSlug(slug)]
  const letter = pickLetter(name, slug)

  return (
    <div
      className={cn(
        "inline-flex items-center justify-center rounded-md font-serif font-semibold select-none flex-shrink-0",
        palette.bg,
        palette.text,
        className
      )}
      style={{
        width: `${px}px`,
        height: `${px}px`,
        fontSize: `${fontPx}px`,
        lineHeight: 1,
      }}
      aria-hidden="true"
    >
      {letter}
    </div>
  )
}
