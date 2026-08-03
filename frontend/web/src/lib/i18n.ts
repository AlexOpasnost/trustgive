import i18n from "i18next"
import { initReactI18next } from "react-i18next"

import enCommon from "@/locales/en.json"
import ruCommon from "@/locales/ru.json"
import { usePreferences } from "@/store/preferences"

/**
 * Language is stored in exactly one place: the `usePreferences` store.
 *
 * It used to be stored in two. zustand persisted `lang` under
 * `trustgive.preferences` and drove every *data* field — `name[lang]`, date
 * formatting — while i18next persisted its own copy under `trustgive.lang` via
 * LanguageDetector and drove every *interface* string. The toggle wrote both, so
 * switching looked fine.
 *
 * Reloading did not. `lng: "en"` was passed to init, and i18next skips the
 * detector entirely when an explicit `lng` is given — the comment next to it
 * claimed "LanguageDetector still wins if it finds localStorage", which is
 * simply not how i18next behaves. So after a reload the store said RU and
 * i18next said EN, and a Russian reader got Russian charity names and dates
 * inside an English interface.
 *
 * Two persisted keys that must agree is the defect; the reload was only where it
 * showed. Now the store is authoritative, i18next is initialised from it, and a
 * subscription pushes later changes one way — store → i18next. There is nothing
 * left to disagree.
 *
 * Behaviour preserved from v3.0: a first-time visitor gets EN regardless of
 * browser locale (the store's default), because a US donor whose Chrome reports
 * CA-FR should not land in Russian. RU stays opt-in via the nav toggle.
 */

const initialLang = usePreferences.getState().lang

void i18n.use(initReactI18next).init({
  fallbackLng: "en",
  lng: initialLang,
  supportedLngs: ["en", "ru"],
  resources: {
    en: { translation: enCommon },
    ru: { translation: ruCommon },
  },
  interpolation: { escapeValue: false },
})

/** Keep the document language in step — screen readers and Google both read it. */
function syncDocumentLang(lang: string): void {
  if (typeof document !== "undefined") {
    document.documentElement.lang = lang
  }
}

syncDocumentLang(initialLang)

usePreferences.subscribe((state, previous) => {
  if (state.lang === previous.lang) return
  void i18n.changeLanguage(state.lang)
  syncDocumentLang(state.lang)
})

export default i18n
