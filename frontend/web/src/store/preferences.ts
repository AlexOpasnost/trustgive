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
 * Persisted to `trustgive.preferences`. The TopNav lang toggle still updates
 * both this store and i18next.
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
