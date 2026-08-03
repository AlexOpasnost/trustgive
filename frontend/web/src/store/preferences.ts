import { create } from "zustand"
import { persist } from "zustand/middleware"

export type Lang = "en" | "ru"
export type ColorScheme = "light" | "dark" | "system"

type PreferencesState = {
  lang: Lang
  colorScheme: ColorScheme
  setLang: (lang: Lang) => void
  setColorScheme: (scheme: ColorScheme) => void
}

/**
 * v3.0: hard EN default. RU is opt-in via the nav toggle.
 *
 * Persisted to `trustgive.preferences`, and since v3.24 this is the *only* place
 * the language lives. `lib/i18n` initialises i18next from it and subscribes for
 * later changes, so callers set `lang` here and nothing else — see the note in
 * lib/i18n.ts for the reload bug that came of having two stores.
 */
export const usePreferences = create<PreferencesState>()(
  persist(
    (set) => ({
      lang: "en",
      colorScheme: "system",
      setLang: (lang) => set({ lang }),
      setColorScheme: (scheme) => set({ colorScheme: scheme }),
    }),
    {
      name: "trustgive.preferences",
    }
  )
)
