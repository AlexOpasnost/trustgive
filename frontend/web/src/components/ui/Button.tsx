/**
 * Button — three-tier hierarchy per DESIGN.md v2.0 §E.
 *
 * Tiers:
 *   - primary   → forest-green filled, the single most important action (donate)
 *   - secondary → outlined ink, transparent fill that flips on hover
 *   - tertiary  → underline link, inherits surrounding text size
 *
 * Polymorphic via `as` prop:
 *   - <Button>...</Button>            renders as <button type="button">
 *   - <Button as="a" href="...">      renders as <a>
 *
 * Loading state (`loading` prop):
 *   - replaces children with a spinner
 *   - sets aria-busy="true"
 *   - locks min-width via inline style to prevent layout shift
 */

import { Loading03Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { cva, type VariantProps } from "class-variance-authority"
import {
  forwardRef,
  type AnchorHTMLAttributes,
  type ButtonHTMLAttributes,
  type ElementType,
  type ReactNode,
} from "react"

import { cn } from "@/lib/utils"

export const buttonVariants = cva(
  // Base — applies to every tier. Min-height 44px (KB-DESIGNER-INIT-002 tap target).
  "inline-flex items-center justify-center gap-2 font-medium transition-colors focus-visible:outline-none disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        primary: cn(
          "bg-verified text-verified-on rounded-md",
          "hover:bg-verified/90",
          "active:bg-verified/80",
          "disabled:bg-rule disabled:text-ink-3"
        ),
        secondary: cn(
          "bg-transparent text-ink border border-ink rounded-md",
          "hover:bg-ink hover:text-paper",
          "active:bg-ink-2 active:text-paper",
          "disabled:border-rule disabled:text-ink-3 disabled:hover:bg-transparent disabled:hover:text-ink-3"
        ),
        tertiary: cn(
          "bg-transparent p-0 text-ink underline decoration-rule decoration-1 underline-offset-4",
          "hover:decoration-ink",
          "active:text-ink-2 active:decoration-ink",
          "disabled:text-ink-3 disabled:no-underline"
        ),
      },
      size: {
        sm: "text-body-sm py-2 px-4 min-h-[36px]",
        md: "text-body-sm py-2.5 px-5 min-h-[44px]",
        lg: "text-body py-3 px-6 min-h-[48px]",
      },
    },
    compoundVariants: [
      // Tertiary always inherits font size from surrounding text and skips padding
      { variant: "tertiary", size: "sm", className: "p-0 min-h-0 text-body-sm" },
      { variant: "tertiary", size: "md", className: "p-0 min-h-0 text-body" },
      { variant: "tertiary", size: "lg", className: "p-0 min-h-0 text-body" },
    ],
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
)

type ButtonOwnProps = VariantProps<typeof buttonVariants> & {
  loading?: boolean
  children?: ReactNode
  className?: string
}

type ButtonAsButton = ButtonOwnProps & {
  as?: "button"
} & Omit<ButtonHTMLAttributes<HTMLButtonElement>, keyof ButtonOwnProps>

type ButtonAsAnchor = ButtonOwnProps & {
  as: "a"
} & Omit<AnchorHTMLAttributes<HTMLAnchorElement>, keyof ButtonOwnProps>

export type ButtonProps = ButtonAsButton | ButtonAsAnchor

export const Button = forwardRef<HTMLElement, ButtonProps>(function Button(
  props,
  ref
) {
  const {
    as,
    variant,
    size,
    loading,
    className,
    children,
    ...rest
  } = props as ButtonOwnProps & {
    as?: ElementType
    [key: string]: unknown
  }

  const Tag: ElementType = (as as ElementType | undefined) ?? "button"
  const classes = cn(buttonVariants({ variant, size }), className)

  // Default `type="button"` on a <button> tag so it doesn't accidentally submit forms.
  const tagProps: Record<string, unknown> = { ...rest }
  if (Tag === "button" && tagProps.type == null) {
    tagProps.type = "button"
  }

  if (loading) {
    tagProps["aria-busy"] = true
    return (
      <Tag
        ref={ref as never}
        className={cn(classes, "relative")}
        {...tagProps}
        // Disable the inner element if it's a button — anchors don't have `disabled`.
        {...(Tag === "button" ? { disabled: true } : {})}
      >
        <span className="invisible inline-flex items-center gap-2" aria-hidden="true">
          {children}
        </span>
        <span className="absolute inset-0 inline-flex items-center justify-center">
          <HugeiconsIcon
            icon={Loading03Icon}
            size={16}
            className="animate-spin"
            aria-hidden="true"
          />
          <span className="sr-only">Loading…</span>
        </span>
      </Tag>
    )
  }

  return (
    <Tag ref={ref as never} className={classes} {...tagProps}>
      {children}
    </Tag>
  )
})
