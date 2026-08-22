import type { Locale } from 'date-fns'
import {
  // be,
  bg,
  // bn,
  ca,
  cs,
  // da,
  de,
  enUS,
  es,
  eu,
  // fi,
  fr,
  gl,
  hr,
  it,
  nb,
  nl,
  pl,
  pt,
  ru,
  // sl,
  // sv,
  // ta,
  tr,
  zhCN,
} from 'date-fns/locale'

import type { TLanguage } from '@/types/locales'

export const isLanguageSupported = (
  language: string
): language is TLanguage => {
  return [
    // 'be',
    'bg',
    // 'bn',
    'ca',
    'cs',
    // 'da',
    'de',
    'en',
    'es',
    'eu',
    // 'fi',
    'fr',
    'gl',
    'hr',
    'it',
    // 'kab',
    'nb',
    'nl',
    'pl',
    'pt',
    'ru',
    // 'sl',
    // 'ta',
    'tr',
    // 'sv',
    'zh_Hans',
  ].includes(language)
}

export const localeFromLanguage: Record<TLanguage, Locale> = {
  // be: be,
  bg: bg,
  // bn: bn,
  ca: ca,
  cs: cs,
  // da: da,
  de: de,
  en: enUS,
  es: es,
  eu: eu,
  // fi: fi,
  fr: fr,
  gl: gl,
  hr: hr,
  it: it,
  kab: enUS, // fallback: date-fns has no Kabyle locale
  nb: nb,
  nl: nl,
  pl: pl,
  pt: pt,
  ru: ru,
  // sl: sl,
  // sv: sv,
  // ta: ta,
  tr: tr,
  zh_Hans: zhCN,
}

export const languageLabels: Record<TLanguage, string> = {
  // be: 'Беларуская мова', // Belarusian
  bg: 'български (50%)', // Bulgarian
  // bn: 'বাংলা',  // Bengali
  ca: 'Català (58%)', // Catalan
  cs: 'Česky (49%)', // Czech
  // da: 'Dansk', // Danish
  de: 'Deutsch', // German
  en: 'English',
  es: 'Español (67%)', // Spanish
  eu: 'Euskara (97%)', // Basque
  fr: 'Français', // French
  gl: 'Galego', // Galician
  hr: 'Hrvatski', // Croatian
  it: 'Italiano (97%)', // Italian
  nl: 'Nederlands', // Dutch
  nb: 'Norsk bokmål (42%)', // Norwegian Bokmål
  pl: 'Polski (93%)', // Polish
  pt: 'Português (50%)', // Portuguese
  ru: 'Русский (94%)', // Russian
  // sl: 'Slovenščina', // Slovenian
  // sv: 'Svenska', // Swedish
  // fi: 'Suomi', // Finnish
  kab: 'Taqbaylit (5%)', // Kabyle
  tr: 'Türkçe (1%)', // Turkish
  // ta: 'தமிழ்', // Tamil
  zh_Hans: '中文（简体）', // Chinese (Simplified Han script)
}

export const availableLanguages = Object.keys(languageLabels).map((l) => {
  return { label: languageLabels[l as TLanguage], value: l }
})
