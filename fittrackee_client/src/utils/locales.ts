import type { Locale } from 'date-fns'
import { de, enUS, es, eu, fr, gl, it, nb, nl, pl } from 'date-fns/locale'

import createI18n from '@/i18n'
import type { TLanguage } from '@/types/locales'

export const isLanguageSupported = (
  language: string
): language is TLanguage => {
  return ['de', 'en', 'es', 'eu', 'fr', 'gl', 'it', 'nb', 'nl', 'pl'].includes(
    language
  )
}

export const localeFromLanguage: Record<TLanguage, Locale> = {
  de: de,
  en: enUS,
  es: es,
  eu: eu,
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
  eu: 'Euskara',
  fr: 'Français',
  gl: 'Galego',
  it: 'Italiano (84%)',
  nb: 'Norsk bokmål (60%)',
  nl: 'Nederlands',
  pl: 'Polski',
}

const { availableLocales } = createI18n.global
export const availableLanguages = availableLocales.map((l) => {
  return { label: languageLabels[l], value: l }
})
