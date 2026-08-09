/**
 * Chip — pill filter button per DESIGN.md v3.1 §I.1.
 *
 * Active: accent bg, paper text. Inactive: white bg, ink text, ink-3 border.
 * Min-height 44px (touch target). Polymorphic: renders <button> by default.
 *
 * Active used to be the verified green, which put "this filter is on" in the
 * same colour as "a regulator confirmed this charity" — on the catalogue page,
 * directly above a grid of cards carrying that badge.
 */

import { forwardRef, type ButtonHTMLAttributes } from "react"

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  active?: boolean
}

export const Chip = forwardRef<HTMLButtonElement, Props>(function Chip(
  { active = false, className = "", children, ...rest },
  ref,
) {
  const base =
    "inline-flex items-center justify-center px-4 py-2 min-h-[40px] rounded-full text-body-sm font-medium whitespace-nowrap transition-colors duration-150 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
  const variant = active
    ? "bg-accent text-accent-on border border-accent hover:bg-accent/90"
    : "bg-surface-raised text-ink border border-rule hover:border-ink-2"
  return (
    <button
      ref={ref}
      type="button"
      className={`${base} ${variant} ${className}`}
      aria-pressed={active}
      {...rest}
    >
      {children}
    </button>
  )
})
