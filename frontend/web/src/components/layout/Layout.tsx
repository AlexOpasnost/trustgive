import { Outlet } from "react-router-dom"

import { Footer } from "./Footer"
import { TopNav } from "./TopNav"

export function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-paper text-ink">
      <TopNav />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
