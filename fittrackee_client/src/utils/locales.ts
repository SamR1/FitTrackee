import type { Locale } from 'date-fns'
import {
  bg,
  // bn,
  ca,
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
  tr,
  zhCN,
} from 'date-fns/locale'

import type { TLanguage } from '@/types/locales'

export const isLanguageSupported = (
  language: string
): language is TLanguage => {
  return [
    'bg',
    // 'bn',
    'ca',
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
    'tr',
    'zh_Hans',
  ].includes(language)
}

export const localeFromLanguage: Record<TLanguage, Locale> = {
  bg: bg,
  // bn: bn,
  ca: ca,
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
  tr: tr,
  zh_Hans: zhCN,
}

export const languageLabels: Record<TLanguage, string> = {
  bg: 'български (54%)', // Bulgarian
  // bn: 'বাংলা',  // Bengali
  ca: 'Català (26%)', // Catalan
  cs: 'Česky (48%)', // Czech
  de: 'Deutsch (93%)', // German
  en: 'English',
  es: 'Español (71%)', // Spanish
  eu: 'Euskara', // Basque
  fr: 'Français', // French
  gl: 'Galego', // Galician
  hr: 'Hrvatski', // Croatian
  it: 'Italiano (99%)', // Italian
  nl: 'Nederlands (99%)', // Dutch
  nb: 'Norsk bokmål (45%)', // Norwegian Bokmål
  pl: 'Polski (95%)', // Polish
  pt: 'Português (53%)', // Portuguese
  ru: 'Русский (95%)', // Russian
  tr: 'Türkçe (1%)', // Turkish
  zh_Hans: '中文（简体）(98%)', // Chinese (Simplified Han script)
}

export const availableLanguages = Object.keys(languageLabels).map((l) => {
  return { label: languageLabels[l as TLanguage], value: l }
})
