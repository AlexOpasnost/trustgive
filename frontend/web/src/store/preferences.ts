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

export const usePreferences = create<PreferencesState>()(
  persist(
    (set) => ({
      lang: (typeof navigator !== "undefined" && navigator.language?.startsWith("ru") ? "ru" : "en") as Lang,
      colorScheme: "system",
      setLang: (lang) => set({ lang }),
      setColorScheme: (scheme) => set({ colorScheme: scheme }),
    }),
    {
      name: "trustgive.preferences",
    }
  )
)
