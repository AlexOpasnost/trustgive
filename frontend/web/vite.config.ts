import path from "node:path"
import { fileURLToPath } from "node:url"

import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: true, // bind to all interfaces (IPv4 + IPv6) — fixes Windows localhost ERR_CONNECTION_REFUSED
    strictPort: true,
    proxy: {
      "/api": {
        target: process.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
        // In production the SPA and the API are different hosts
        // (trustgive.org vs api.trustgive.org), so the site is free to have a
        // page at /api — and since v3.22 it does: the public API
        // documentation. In development this proxy stands in for that host
        // split and would swallow the route, serving DRF's root listing
        // instead of the page. Bypassing the two spellings of the page itself
        // restores it; everything deeper ("/api/charities/", "/api/stats/")
        // still proxies. Browsers normalise "/api" to "/api/", so both forms
        // have to be handled.
        bypass(req) {
          const path = (req.url ?? "").split("?")[0]
          if (path === "/api" || path === "/api/") return "/index.html"
          return undefined
        },
      },
    },
  },
  build: {
    target: "es2022",
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          "react-vendor": ["react", "react-dom", "react-router-dom"],
          "query-vendor": ["@tanstack/react-query", "openapi-fetch"],
          "ui-vendor": [
            "@radix-ui/react-dialog",
            "@radix-ui/react-popover",
            "@radix-ui/react-tabs",
            "@radix-ui/react-tooltip",
          ],
          "icons-vendor": ["@hugeicons/react", "@hugeicons/core-free-icons"],
          "charts-vendor": ["recharts"],
          "i18n-vendor": ["i18next", "react-i18next", "i18next-browser-languagedetector"],
        },
      },
    },
  },
})
