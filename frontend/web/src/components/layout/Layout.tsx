import { Outlet } from "react-router-dom"

import { Footer } from "./Footer"
import { TopNav } from "./TopNav"

export function Layout() {
  return (
    <div
      className="min-h-screen flex flex-col"
      style={{
        background: "var(--color-paper-v4)",
        color: "var(--color-ink-v4)",
      }}
    >
      <TopNav />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
