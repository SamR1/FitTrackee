import type { Locale } from 'date-fns'
import {
  bg,
  // bn,
  cs,
  de,
  enUS,
  es,
  eu,
  fr,
  gl,
  hr,
  it,
  nb,
  nl,
  pl,
  pt,
  ru,
  zhCN,
} from 'date-fns/locale'

import type { TLanguage } from '@/types/locales'

export const isLanguageSupported = (
  language: string
): language is TLanguage => {
  return [
    'bg',
    // 'bn',
    'cs',
    'de',
    'en',
    'es',
    'eu',
    'fr',
    'gl',
    'hr',
    'it',
    'nb',
    'nl',
    'pl',
    'pt',
    'ru',
    'zh_Hans',
  ].includes(language)
}

export const localeFromLanguage: Record<TLanguage, Locale> = {
  bg: bg,
  // bn: bn,
  cs: cs,
  de: de,
  en: enUS,
  es: es,
  eu: eu,
  fr: fr,
  gl: gl,
  hr: hr,
  it: it,
  nb: nb,
  nl: nl,
  pl: pl,
  pt: pt,
  ru: ru,
  zh_Hans: zhCN,
}

export const languageLabels: Record<TLanguage, string> = {
  bg: 'български (62%)',
  // bn: 'বাংলা',
  cs: 'Česky (46%)',
  de: 'Deutsch (98%)',
  en: 'English',
  es: 'Español (64%)',
  eu: 'Euskara',
  fr: 'Français',
  gl: 'Galego',
  hr: 'Hrvatski',
  it: 'Italiano (51%)',
  nl: 'Nederlands',
  nb: 'Norsk bokmål (33%)',
  pl: 'Polski (99%)',
  pt: 'Português (61%)',
  ru: 'Русский (69%)',
  zh_Hans: '中文（简体）(99%)',
}

export const availableLanguages = Object.keys(languageLabels).map((l) => {
  return { label: languageLabels[l as TLanguage], value: l }
})
