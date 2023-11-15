import type { Locale } from 'date-fns'
import { de, enUS, es, fr, gl, it, nb, nl, pl } from 'date-fns/locale'

import createI18n from '@/i18n'
import type { TLanguage } from '@/types/locales'

export const isLanguageSupported = (
  language: string
): language is TLanguage => {
  return (
    language === 'de' ||
    language === 'en' ||
    language === 'es' ||
    language === 'fr' ||
    language === 'gl' ||
    language === 'it' ||
    language === 'nb' ||
    language === 'nl' ||
    language === 'pl'
  )
}

export const localeFromLanguage: Record<TLanguage, Locale> = {
  de: de,
  en: enUS,
  es: es,
  fr: fr,
  gl: gl,
  it: it,
  nb: nb,
  nl: nl,
  pl: pl,
}

export const languageLabels: Record<TLanguage, string> = {
  de: 'Deutsch',
  en: 'English',
  es: 'Español',
  fr: 'Français',
  gl: 'Galego',
  it: 'Italiano (85%)',
  nb: 'Norsk bokmål (35%)',
  nl: 'Nederlands',
  pl: 'Polski',
}

const { availableLocales } = createI18n.global
export const availableLanguages = availableLocales.map((l) => {
  return { label: languageLabels[l], value: l }
})
