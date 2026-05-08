/**
 * Chip — pill filter button per DESIGN.md v3.1 §I.1.
 *
 * Active: forest green bg, white text. Inactive: white bg, ink text, ink-3 border.
 * Min-height 44px (touch target). Polymorphic: renders <button> by default.
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
    "inline-flex items-center justify-center px-4 py-2 min-h-[40px] rounded-full text-body-sm font-medium whitespace-nowrap transition-colors duration-150 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-verified focus-visible:ring-offset-2"
  const variant = active
    ? "bg-verified text-paper border border-verified hover:bg-verified/90"
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
