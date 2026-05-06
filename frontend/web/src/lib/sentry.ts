/**
 * Sentry frontend wiring (per ADR-008).
 *
 * Initialised once from main.tsx — no-op when VITE_SENTRY_DSN is unset
 * (typical in local dev). Production builds always set it via Cloudflare
 * Pages env vars.
 */
import * as Sentry from "@sentry/react"

const DSN = import.meta.env.VITE_SENTRY_DSN as string | undefined
const ENV = (import.meta.env.MODE as string) || "development"

export function initSentry(): void {
  if (!DSN) return

  Sentry.init({
    dsn: DSN,
    environment: ENV,
    tracesSampleRate: 0,
    replaysSessionSampleRate: 0,
    replaysOnErrorSampleRate: 0.1,
    sendDefaultPii: false,
    beforeSend(event) {
      // Strip request body from errors — defence-in-depth
      if (event.request) {
        delete event.request.cookies
        delete event.request.data
      }
      return event
    },
  })
}

export const sentry = Sentry
