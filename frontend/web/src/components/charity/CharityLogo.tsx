/**
 * CharityLogo — fallback chain per DESIGN.md v2.0 §D.3.
 *
 *   1. logo_url present + image loads     → render <img>
 *   2. logo_url null OR image errors      → BrandedAvatar
 *
 * Visual rules (§D.2):
 *   - Container: white surface-raised inside a rounded squircle (logos are
 *     designed for white backgrounds; tinted bg = brand vandalism).
 *   - object-contain (never object-cover) — cropping a wordmark is brand vandalism.
 *   - Internal padding so the logo never touches the rounded edge.
 */

import { useEffect, useState } from "react"

import { BrandedAvatar, type BrandedAvatarSize } from "@/components/ui/BrandedAvatar"
import { cn } from "@/lib/utils"

type Props = {
  logoUrl?: string | null
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

// Internal padding inside the squircle (DESIGN.md §D.2): logos breathe.
const PADDING_PX: Record<BrandedAvatarSize, number> = {
  sm: 3,
  md: 4,
  lg: 6,
  xl: 8,
}

export function CharityLogo({ logoUrl, slug, name, size = "md", className }: Props) {
  const [errored, setErrored] = useState(false)
  const px = SIZE_PX[size]
  const padPx = PADDING_PX[size]

  // Reset error state if the URL changes (e.g. swapping between charities in a list).
  useEffect(() => {
    setErrored(false)
  }, [logoUrl])

  const hasUrl = typeof logoUrl === "string" && logoUrl.length > 0

  if (!hasUrl || errored) {
    return <BrandedAvatar slug={slug} name={name} size={size} className={className} />
  }

  return (
    <div
      className={cn(
        "inline-flex items-center justify-center rounded-md bg-surface-raised border border-rule flex-shrink-0 overflow-hidden",
        className
      )}
      style={{
        width: `${px}px`,
        height: `${px}px`,
        padding: `${padPx}px`,
      }}
    >
      <img
        src={logoUrl as string}
        alt={name}
        loading="lazy"
        decoding="async"
        onError={() => setErrored(true)}
        className="max-w-full max-h-full object-contain"
        style={{ display: "block" }}
      />
    </div>
  )
}
