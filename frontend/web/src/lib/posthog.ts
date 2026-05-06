/**
 * PostHog client-side analytics — no-op when VITE_POSTHOG_API_KEY is unset.
 *
 * Server-side mirror for the donation_redirect event lives in apps/core/posthog.py
 * (per ADR-008) — it makes the conversion event ad-block resistant.
 */
import posthog from "posthog-js"

const KEY = import.meta.env.VITE_POSTHOG_API_KEY as string | undefined
const HOST = (import.meta.env.VITE_POSTHOG_HOST as string | undefined) || "https://eu.i.posthog.com"

let initialised = false

export function initPostHog(): void {
  if (!KEY || initialised) return
  posthog.init(KEY, {
    api_host: HOST,
    person_profiles: "identified_only",
    capture_pageview: true,
    capture_pageleave: true,
    autocapture: false, // we'll capture explicitly to keep payloads tight
    disable_session_recording: true,
  })
  initialised = true
}

type EventProps = Record<string, string | number | boolean | null | undefined>

export function track(event: string, props: EventProps = {}): void {
  if (!initialised) return
  posthog.capture(event, props as Record<string, unknown>)
}
