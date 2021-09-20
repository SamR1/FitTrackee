/* eslint-disable import/no-duplicates */
import { Locale } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'

export const localeFromLanguage: Record<string, Locale> = {
  en: enUS,
  fr: fr,
}
