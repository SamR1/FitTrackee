/* eslint-disable import/no-duplicates */
import { Locale } from 'date-fns'
import { de, enUS, fr, it, nl } from 'date-fns/locale'

import createI18n from '@/i18n'

export const localeFromLanguage: Record<string, Locale> = {
  de: de,
  en: enUS,
  // es: es, // disabled for now
  fr: fr,
  // gl: gl, // disabled for now
  it: it,
  // nb: nb, // disabled for now
  nl: nl,
}

export const languageLabels: Record<string, string> = {
  de: 'Deutsch',
  en: 'English',
  // es: 'Español', // disabled for now
  fr: 'Français',
  // gl: 'Galego', // disabled for now
  it: 'Italiano',
  // nb: 'Norsk bokmål', // disabled for now
  nl: 'Nederlands',
}

const { availableLocales } = createI18n.global
export const availableLanguages = availableLocales.map((l) => {
  return { label: languageLabels[l], value: l }
})
