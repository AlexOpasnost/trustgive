/// <reference types="vite/client" />

/**
 * Vite ambient types — gives TS knowledge of:
 *  - CSS / asset imports (`import "./index.css"`, `import logo from "./logo.svg"`)
 *  - `import.meta.env.VITE_*` strings injected at build time
 */

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_SENTRY_DSN?: string
  readonly VITE_POSTHOG_API_KEY?: string
  readonly VITE_POSTHOG_HOST?: string
  readonly MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
