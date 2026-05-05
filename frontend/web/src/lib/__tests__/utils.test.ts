import { describe, expect, it } from "vitest"

import { cn, formatPercent, formatUsd } from "@/lib/utils"

describe("cn", () => {
  it("merges tailwind classes", () => {
    expect(cn("px-2", "px-4")).toBe("px-4")
  })
  it("filters falsy", () => {
    expect(cn("a", false, null, "b")).toBe("a b")
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
