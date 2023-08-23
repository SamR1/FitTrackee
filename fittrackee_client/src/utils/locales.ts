/* eslint-disable import/no-duplicates */
import { Locale } from 'date-fns'
import { de, enUS, es, fr, gl, it, nb, nl, pl } from 'date-fns/locale'

import createI18n from '@/i18n'

export const localeFromLanguage: Record<string, Locale> = {
  de: de,
  en: enUS,
  es: es,
  fr: fr,
  gl: gl,
  it: it,
  pl: pl,
  nb: nb,
  nl: nl,
}

export const languageLabels: Record<string, string> = {
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
