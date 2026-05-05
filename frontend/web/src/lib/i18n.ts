import i18n from "i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import { initReactI18next } from "react-i18next"

import enCommon from "@/locales/en.json"
import ruCommon from "@/locales/ru.json"

void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: "en",
    supportedLngs: ["en", "ru"],
    resources: {
      en: { translation: enCommon },
      ru: { translation: ruCommon },
    },
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      lookupLocalStorage: "trustgive.lang",
      caches: ["localStorage"],
    },
  })

export default i18n
