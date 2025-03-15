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
  ru,
  zhCN,
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
    'ru',
    'zh_Hans',
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
  ru: ru,
  zh_Hans: zhCN,
}

export const languageLabels: Record<TLanguage, string> = {
  bg: 'български (63%)',
  cs: 'Česky (46%)',
  de: 'Deutsch (85%)',
  en: 'English',
  es: 'Español (64%)',
  eu: 'Euskara (81%)',
  fr: 'Français',
  gl: 'Galego (99%)',
  it: 'Italiano (52%)',
  nl: 'Nederlands (64%)',
  nb: 'Norsk bokmål (34%)',
  pl: 'Polski (99%)',
  pt: 'Português (62%)',
  ru: 'Русский (39%)',
  zh_Hans: '中文（简体）(99%)',
}

export const availableLanguages = Object.keys(languageLabels).map((l) => {
  return { label: languageLabels[l as TLanguage], value: l }
})
