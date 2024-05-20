import { createI18n } from 'vue-i18n'

import csMessages from '@/locales/cs/cs'
import deMessages from '@/locales/de/de'
import enMessages from '@/locales/en/en'
import esMessages from '@/locales/es/es'
import euMessages from '@/locales/eu/eu'
import frMessages from '@/locales/fr/fr'
import glMessages from '@/locales/gl/gl'
import itMessages from '@/locales/it/it'
import nbMessages from '@/locales/nb/nb'
import nlMessages from '@/locales/nl/nl'
import plMessages from '@/locales/pl/pl'
// import ptMessages from '@/locales/pt/pt'

export default createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  globalInjection: true,
  messages: {
    cs: csMessages,
    de: deMessages,
    en: enMessages,
    es: esMessages,
    eu: euMessages,
    fr: frMessages,
    gl: glMessages,
    it: itMessages,
    nb: nbMessages,
    nl: nlMessages,
    pl: plMessages,
    // pt: ptMessages,
  },
})
