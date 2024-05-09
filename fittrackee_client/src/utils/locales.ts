import type { Locale } from 'date-fns'
import { cs, de, enUS, es, eu, fr, gl, it, nb, nl, pl } from 'date-fns/locale'

import createI18n from '@/i18n'
import type { TLanguage } from '@/types/locales'

export const isLanguageSupported = (
  language: string
): language is TLanguage => {
  return [
    'cs',
    'de',
    'en',
    'es',
    'eu',
    'fr',
    'gl',
    'it',
    'nb',
    'nl',
    'pl',
  ].includes(language)
}

export const localeFromLanguage: Record<TLanguage, Locale> = {
  cs: cs,
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
  cs: 'Česky (25%)',
  de: 'Deutsch',
  en: 'English',
  es: 'Español',
  eu: 'Euskara',
  fr: 'Français',
  gl: 'Galego',
  it: 'Italiano (74%)',
  nb: 'Norsk bokmål (53%)',
  nl: 'Nederlands (98%)',
  pl: 'Polski (88%)',
}

const { availableLocales } = createI18n.global
export const availableLanguages = availableLocales.map((l) => {
  return { label: languageLabels[l], value: l }
})
