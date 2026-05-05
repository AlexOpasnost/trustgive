import { expect, test } from "@playwright/test"

test.describe("Homepage + language switch", () => {
  test("shows hero, 0% callout, and CTAs on first paint", async ({ page }) => {
    await page.goto("/")
    await expect(page.getByRole("heading", { level: 1 })).toContainText(/source documents/i)
    await expect(page.getByText("0%")).toBeVisible()
    await expect(page.getByRole("link", { name: /explore catalog/i })).toBeVisible()
    await expect(page.getByRole("link", { name: /how we verify/i }).first()).toBeVisible()
  })

  test("EN → RU toggle switches all UI strings", async ({ page }) => {
    await page.goto("/")
    await page.getByRole("button", { name: "RU", exact: false }).click()
    await expect(page.getByRole("heading", { level: 1 })).toContainText(
      /исходные документы/i
    )
    // Switch back to EN
    await page.getByRole("button", { name: "EN", exact: false }).click()
    await expect(page.getByRole("heading", { level: 1 })).toContainText(/source documents/i)
  })

  test("navigation to methodology page works", async ({ page }) => {
    await page.goto("/")
    await page.getByRole("link", { name: /methodology/i }).first().click()
    await expect(page).toHaveURL(/\/methodology$/)
    await expect(page.getByRole("heading", { name: /how we verify/i })).toBeVisible()
  })
})
