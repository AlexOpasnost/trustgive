import { defineConfig, devices } from "@playwright/test"

const FRONTEND_URL = process.env.E2E_FRONTEND_URL || "http://localhost:5173"

export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? [["github"], ["html"]] : "list",
  use: {
    baseURL: FRONTEND_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium-desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile-iphone", use: { ...devices["iPhone 14"] } },
  ],
})
