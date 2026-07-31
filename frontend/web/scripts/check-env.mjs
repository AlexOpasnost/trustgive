/**
 * Build-time guard on the public env vars.
 *
 * Why this exists: a production build once shipped with VITE_API_BASE_URL set to
 * a PostHog key. Every API call then went to
 * `https://trustgive.org/phc_…/api/charities/…`, which the SPA fallback answered
 * with index.html and HTTP 200. Nothing threw, nothing logged, and the homepage
 * silently rendered as an empty strip — nav, one paragraph, footer — for however
 * long it took someone to look.
 *
 * The failure was invisible precisely because every layer behaved "correctly":
 * the build succeeded, the deploy succeeded, the server returned 200. So the
 * check has to happen here, before the bundle is written.
 *
 * Runs automatically via the `prebuild` npm script.
 */
import { readFileSync, existsSync } from "node:fs"
import { resolve, dirname } from "node:path"
import { fileURLToPath } from "node:url"

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..")
const mode = process.env.NODE_ENV === "development" ? "development" : "production"

// Vite precedence, lowest to highest. Later files win.
const files = [".env", ".env.local", `.env.${mode}`, `.env.${mode}.local`]

const env = {}
for (const name of files) {
  const path = resolve(root, name)
  if (!existsSync(path)) continue
  for (const line of readFileSync(path, "utf8").split("\n")) {
    const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/)
    if (match) env[match[1]] = match[2].trim().replace(/^["']|["']$/g, "")
  }
}
// A real environment variable outranks every file.
for (const key of Object.keys(env)) {
  if (process.env[key]) env[key] = process.env[key]
}

const errors = []

const api = env.VITE_API_BASE_URL
if (!api) {
  errors.push("VITE_API_BASE_URL is not set — every API call would resolve against the site origin.")
} else if (!/^https?:\/\//.test(api)) {
  errors.push(
    `VITE_API_BASE_URL is "${api}", which is not an absolute URL. ` +
      "Requests would be appended to the site origin and answered by the SPA fallback with HTTP 200, " +
      "so the failure would be silent.",
  )
} else if (/^phc_|^phx_|^cfut_/.test(api)) {
  errors.push(`VITE_API_BASE_URL looks like an API key ("${api.slice(0, 12)}…"), not a URL.`)
}

const posthog = env.VITE_POSTHOG_API_KEY
if (posthog && !/^phc_/.test(posthog)) {
  errors.push(`VITE_POSTHOG_API_KEY should start with "phc_" (client key), got "${posthog.slice(0, 12)}…".`)
}

if (errors.length) {
  console.error("\n  Build stopped — environment is misconfigured:\n")
  for (const e of errors) console.error(`  • ${e}`)
  console.error("")
  process.exit(1)
}

console.log(`  env ok — API ${api}`)
