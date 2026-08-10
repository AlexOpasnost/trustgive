import { usePreferences, type ColorScheme } from "@/store/preferences"

/**
 * Applies the colour scheme to the document. Same shape as lib/i18n: the
 * preferences store is authoritative and this pushes changes one way.
 *
 * Until 2026-08-10 nothing did this. The `.dark` palette in index.css was
 * complete and correct, `colorScheme` was stored and persisted, and no code ever
 * connected the two — so choosing "dark" changed a value in localStorage and not
 * a single pixel. A stored preference that does nothing is worse than no
 * preference, because it reads as a feature.
 *
 * Three states, and "system" is the default:
 *   light   — always the paper palette
 *   dark    — always the ink palette
 *   system  — follow the OS, and keep following it. The media query is watched,
 *             not merely read once, so a laptop switching at sunset moves the
 *             site with it.
 */

const DARK_CLASS = "dark"

function prefersDark(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  )
}

export function resolveScheme(scheme: ColorScheme): "light" | "dark" {
  if (scheme === "system") return prefersDark() ? "dark" : "light"
  return scheme
}

function apply(scheme: ColorScheme): void {
  if (typeof document === "undefined") return
  const root = document.documentElement
  root.classList.toggle(DARK_CLASS, resolveScheme(scheme) === "dark")
  // `color-scheme` makes the browser's own chrome — form controls, scrollbars,
  // the canvas behind the page — match. Without it a dark page keeps white
  // scrollbars and a white flash between navigations.
  root.style.colorScheme = resolveScheme(scheme)
}

/**
 * Wire the store to the document. Called once from main.tsx, before render.
 *
 * The initial class is normally already on `<html>` — index.html sets it inline
 * so the first paint is correct — and this re-applies it from the same source,
 * which also repairs the case where localStorage was written by another tab.
 */
export function initColorScheme(): void {
  apply(usePreferences.getState().colorScheme)

  usePreferences.subscribe((state, previous) => {
    if (state.colorScheme === previous.colorScheme) return
    apply(state.colorScheme)
  })

  if (typeof window !== "undefined" && typeof window.matchMedia === "function") {
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", () => {
        // Only "system" follows the OS; an explicit choice is a choice.
        if (usePreferences.getState().colorScheme === "system") {
          apply("system")
        }
      })
  }
}
