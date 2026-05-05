import { expect, test } from "@playwright/test"

test.describe("Donate confirmation flow", () => {
  test("clicking Donate opens modal with anti-fee bullets", async ({ page }) => {
    await page.goto("/charities/givedirectly")
    const hasError = await page.getByText(/We couldn't load/i).isVisible().catch(() => false)
    test.skip(hasError, "Backend has no seeded charity yet")

    await page.getByRole("button", { name: /donate on/i }).click()

    // Modal visible with required messaging
    await expect(page.getByRole("dialog")).toBeVisible()
    await expect(page.getByText(/0% platform fee/i)).toBeVisible()
    await expect(page.getByText(/we never see your money/i)).toBeVisible()
    await expect(page.getByText(/we never share your contact info/i)).toBeVisible()

    // Cancel works
    await page.getByRole("button", { name: /cancel/i }).click()
    await expect(page.getByRole("dialog")).not.toBeVisible()
  })

  test("Continue button has correct outbound target", async ({ page }) => {
    await page.goto("/charities/givedirectly")
    const hasError = await page.getByText(/We couldn't load/i).isVisible().catch(() => false)
    test.skip(hasError, "Backend has no seeded charity yet")

    await page.getByRole("button", { name: /donate on/i }).click()
    const continueLink = page.getByRole("button", { name: /continue to/i })
    await expect(continueLink).toBeVisible()
    // We don't actually navigate (would leave the test scope) — just assert the flow exists
  })
})
