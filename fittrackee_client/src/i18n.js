import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import XHR from 'i18next-xhr-backend'

import EnTranslations from './locales/en/translations.json'
import FrTranslations from './locales/fr/translations.json'

i18n
  .use(XHR)
  .use(LanguageDetector)
  .init({
    debug: true,
    lng: 'en',
    fallbackLng: 'en',
    keySeparator: false,
    interpolation: {
      escapeValue: false,
    },
    resources: {
      en: {
        translations: EnTranslations,
      },
      fr: {
        translations: FrTranslations,
      },
    },
    ns: ['translations'],
    defaultNS: 'translations',
  })

export default i18n
