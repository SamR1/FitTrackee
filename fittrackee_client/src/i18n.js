import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import XHR from 'i18next-xhr-backend'

import EnCommonTranslations from './locales/en/common.json'
import EnUserTranslations from './locales/en/user.json'
import FrCommonTranslations from './locales/fr/common.json'
import FrUserTranslations from './locales/fr/user.json'

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
        common: EnCommonTranslations,
        user: EnUserTranslations,
      },
      fr: {
        common: FrCommonTranslations,
        user: FrUserTranslations,
      },
    },
    ns: ['common'],
    defaultNS: 'common',
  })

export default i18n
