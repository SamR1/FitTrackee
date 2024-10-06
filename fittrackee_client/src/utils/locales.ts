import type { Locale } from 'date-fns'
import {
  bg,
  cs,
  de,
  enUS,
  es,
  eu,
  fr,
  gl,
  it,
  nb,
  nl,
  pl,
  pt,
  // ru,
} from 'date-fns/locale'

import type { TLanguage } from '@/types/locales'

export const isLanguageSupported = (
  language: string
): language is TLanguage => {
  return [
    'bg',
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
    'pt',
    // 'ru',
  ].includes(language)
}

export const localeFromLanguage: Record<TLanguage, Locale> = {
  bg: bg,
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
  pt: pt,
  // ru: ru,
}

export const languageLabels: Record<TLanguage, string> = {
  bg: 'български (99%)',
  cs: 'Česky (72%)',
  de: 'Deutsch',
  en: 'English',
  es: 'Español',
  eu: 'Euskara',
  fr: 'Français',
  gl: 'Galego',
  it: 'Italiano (82%)',
  nl: 'Nederlands (99%)',
  nb: 'Norsk bokmål (52%)',
  pl: 'Polski (99%)',
  pt: 'Português (97%)',
  // ru: 'Русский',
}

export const availableLanguages = Object.keys(languageLabels).map((l) => {
  return { label: languageLabels[l as TLanguage], value: l }
})
