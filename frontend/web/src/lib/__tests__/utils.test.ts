import { describe, expect, it } from "vitest"

import { cn, formatPercent, formatUsd } from "@/lib/utils"

describe("cn", () => {
  it("merges tailwind classes", () => {
    expect(cn("px-2", "px-4")).toBe("px-4")
  })
  it("filters falsy", () => {
    expect(cn("a", false, null, "b")).toBe("a b")
  })

  // tailwind-merge only knows stock Tailwind names. Everything below is from
  // this project's @theme, and before utils.ts declared the class groups,
  // tailwind-merge guessed — putting colours and sizes in one bucket and
  // deleting whichever came first.
  describe("project tokens", () => {
    it("keeps a text colour and a text size together", () => {
      // The live bug: Button composed `text-verified-on` (colour) with the size
      // variant's `text-body`, and the colour was dropped — leaving the donate
      // label in inherited ink on a green fill.
      const merged = cn("bg-accent text-accent-on rounded-md", "text-body")
      expect(merged).toContain("text-accent-on")
      expect(merged).toContain("text-body")
    })

    it("still lets a later size replace an earlier one", () => {
      expect(cn("text-prose", "text-lead")).toBe("text-lead")
      expect(cn("text-body", "text-caption")).toBe("text-caption")
    })

    it("still lets a later text colour replace an earlier one", () => {
      expect(cn("text-ink-3", "text-ink")).toBe("text-ink")
    })

    it("does not let a size and a colour cancel each other in either order", () => {
      expect(cn("text-lead", "text-ink-2")).toBe("text-lead text-ink-2")
      expect(cn("text-ink-2", "text-lead")).toBe("text-ink-2 text-lead")
    })

    it("separates background and border colours from text colours", () => {
      const merged = cn("bg-verified-soft text-verified border-verified")
      expect(merged).toBe("bg-verified-soft text-verified border-verified")
    })

    it("resolves conflicts within background colours", () => {
      expect(cn("bg-paper", "bg-accent")).toBe("bg-accent")
    })
  })
})

describe("formatUsd", () => {
  it("formats large numbers compactly when requested", () => {
    expect(formatUsd(349_000_000, { compact: true })).toMatch(/\$349\.0M|\$349M/)
  })
  it("returns em-dash for null/undefined", () => {
    expect(formatUsd(null)).toBe("—")
    expect(formatUsd(undefined)).toBe("—")
  })
  it("returns em-dash for invalid input", () => {
    expect(formatUsd("not a number")).toBe("—")
  })
})

describe("formatPercent", () => {
  it("formats with 1 decimal", () => {
    expect(formatPercent(91.0)).toBe("91.0%")
  })
  it("returns em-dash for nullish", () => {
    expect(formatPercent(null)).toBe("—")
  })
})
