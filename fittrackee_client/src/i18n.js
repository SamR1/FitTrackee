import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import XHR from 'i18next-xhr-backend'

import EnActivitiesTranslations from './locales/en/activities.json'
import EnCommonTranslations from './locales/en/common.json'
import EnDashboardTranslations from './locales/en/dashboard.json'
import EnMessagesTranslations from './locales/en/messages.json'
import EnSportsTranslations from './locales/en/sports.json'
import EnStatisticsTranslations from './locales/en/statistics.json'
import EnUserTranslations from './locales/en/user.json'
import FrActivitiesTranslations from './locales/fr/activities.json'
import FrCommonTranslations from './locales/fr/common.json'
import FrDashboardTranslations from './locales/fr/dashboard.json'
import FrMessagesTranslations from './locales/fr/messages.json'
import FrSportsTranslations from './locales/fr/sports.json'
import FrStatisticsTranslations from './locales/fr/statistics.json'
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
        activities: EnActivitiesTranslations,
        common: EnCommonTranslations,
        dashboard: EnDashboardTranslations,
        messages: EnMessagesTranslations,
        sports: EnSportsTranslations,
        statistics: EnStatisticsTranslations,
        user: EnUserTranslations,
      },
      fr: {
        activities: FrActivitiesTranslations,
        common: FrCommonTranslations,
        dashboard: FrDashboardTranslations,
        messages: FrMessagesTranslations,
        sports: FrSportsTranslations,
        statistics: FrStatisticsTranslations,
        user: FrUserTranslations,
      },
    },
    ns: ['common'],
    defaultNS: 'common',
  })

export default i18n
