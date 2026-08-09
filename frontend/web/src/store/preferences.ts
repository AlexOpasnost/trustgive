import { create } from "zustand"
import { persist } from "zustand/middleware"

export type Lang = "en" | "ru"

/**
 * Stored, persisted to localStorage — and read by nobody.
 *
 * Nothing in the app puts the `dark` class on the document, and no component
 * uses a `dark:` variant, so `setColorScheme("dark")` writes a value that
 * changes no pixel. The `.dark` palette in index.css is complete and correct
 * (verified 2026-08-05 by mounting a probe inside a `.dark` wrapper), it is
 * simply never switched on.
 *
 * Left in place rather than deleted: the palette is real work and the decision
 * to ship dark mode is the operator's, not a side effect of a typography pass.
 * But it is recorded here so the next reader does not assume, as the type name
 * invites, that this preference does something.
 */
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
