import { render, screen } from "@testing-library/react"
import { I18nextProvider } from "react-i18next"
import { describe, expect, it } from "vitest"

import { VerificationBadge } from "@/components/charity/VerificationBadge"
import i18n from "@/lib/i18n"

const wrap = (ui: React.ReactElement) => render(<I18nextProvider i18n={i18n}>{ui}</I18nextProvider>)

describe("VerificationBadge", () => {
  it("renders 'Verified' label for verified status", () => {
    wrap(<VerificationBadge status="verified" />)
    expect(screen.getByText(/verified/i)).toBeInTheDocument()
  })

  it("renders 'Listed' for listed status", () => {
    wrap(<VerificationBadge status="listed" />)
    expect(screen.getByText(/listed/i)).toBeInTheDocument()
  })

  it("includes screen-reader-only context", () => {
    wrap(<VerificationBadge status="verified" />)
    expect(screen.getByText(/verification status/i)).toBeInTheDocument()
  })
})
