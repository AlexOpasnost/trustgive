import { expect, test } from "@playwright/test"

test.describe("Catalog → Detail → Source-document drawer", () => {
  test("user can open catalog and see filter UI", async ({ page }) => {
    await page.goto("/charities")
    await expect(page.getByRole("heading", { name: /charities/i })).toBeVisible()
    // Filter sidebar present
    await expect(page.getByText(/country/i)).toBeVisible()
    await expect(page.getByText(/size/i)).toBeVisible()
  })

  test("filter persists in URL on country selection", async ({ page }) => {
    await page.goto("/charities")
    await page.getByLabel("United States").check()
    await expect(page).toHaveURL(/country=US/)
  })

  test("source-document drawer opens on charity detail page", async ({ page }) => {
    // This test requires a seeded charity with at least 1 source document.
    // Skip if backend has no data yet.
    await page.goto("/charities/givedirectly")
    const hasError = await page.getByText(/We couldn't load/i).isVisible().catch(() => false)
    test.skip(hasError, "Backend has no seeded charity yet")

    const docLink = page.getByText(/IRS Form 990/i).first()
    await docLink.click()
    await expect(page.getByRole("dialog")).toBeVisible()
    await expect(page.getByText(/original filing/i)).toBeVisible()

    // ESC closes the drawer (Radix Dialog)
    await page.keyboard.press("Escape")
    await expect(page.getByRole("dialog")).not.toBeVisible()
  })
})
