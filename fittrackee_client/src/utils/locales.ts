/* eslint-disable import/no-duplicates */
import { Locale } from 'date-fns'
import { de, enUS, fr, nl } from 'date-fns/locale'

import createI18n from '@/i18n'

export const localeFromLanguage: Record<string, Locale> = {
  de: de,
  en: enUS,
  fr: fr,
  // nb: nb, // disabled for now
  nl: nl,
}

export const languageLabels: Record<string, string> = {
  de: 'Deutsch',
  en: 'English',
  fr: 'Français',
  // nb: 'Norsk bokmål', // disabled for now
  nl: 'Nederlands',
}

const { availableLocales } = createI18n.global
export const availableLanguages = availableLocales.map((l) => {
  return { label: languageLabels[l], value: l }
})
