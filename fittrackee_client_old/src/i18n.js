import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import XHR from 'i18next-xhr-backend'

import { resources } from './locales'

i18n
  .use(XHR)
  .use(LanguageDetector)
  .init({
    debug: process.env.NODE_ENV === 'development',
    lng: 'en',
    fallbackLng: 'en',
    keySeparator: false,
    interpolation: {
      escapeValue: false,
    },
    resources,
    ns: ['common'],
    defaultNS: 'common',
  })

export default i18n
