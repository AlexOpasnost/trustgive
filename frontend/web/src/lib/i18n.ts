import i18n from "i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import { initReactI18next } from "react-i18next"

import enCommon from "@/locales/en.json"
import ruCommon from "@/locales/ru.json"

/**
 * v3.0: default language is EN regardless of browser locale.
 * - localStorage override (`trustgive.lang`) honored when present.
 * - First-time visitor (no localStorage entry) → EN, period.
 * - Navigator detection is intentionally OMITTED so a US donor whose Chrome
 *   thinks they're in CA-FR doesn't land in RU. Real RU users opt in via the
 *   nav toggle.
 */
void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: "en",
    lng: "en", // hard default; LanguageDetector still wins if it finds localStorage
    supportedLngs: ["en", "ru"],
    resources: {
      en: { translation: enCommon },
      ru: { translation: ruCommon },
    },
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage"],
      lookupLocalStorage: "trustgive.lang",
      caches: ["localStorage"],
    },
  })

export default i18n
