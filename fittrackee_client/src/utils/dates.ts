import {
  addDays,
  addMonths,
  addYears,
  endOfMonth,
  endOfWeek,
  format,
  intlFormat,
  startOfMonth,
  startOfWeek,
  startOfYear,
} from 'date-fns'
import type { IntlFormatFormatOptions } from 'date-fns'
import { toZonedTime } from 'date-fns-tz'

import createI18n from '@/i18n'
import type { TLanguage } from '@/types/locales'
import { localeFromLanguage } from '@/utils/locales'

const { locale } = createI18n.global

export const getStartDate = (
  duration: string,
  day: Date,
  weekStartingMonday: boolean
): Date => {
  switch (duration) {
    case 'day':
      return day
    case 'week':
      return startOfWeek(day, { weekStartsOn: weekStartingMonday ? 1 : 0 })
    case 'year':
      return startOfYear(day)
    case 'month':
      return startOfMonth(day)
    default:
      throw new Error(
        `Invalid duration, expected: "day", "week", "month", "year", got: "${duration}"`
      )
  }
}

export const incrementDate = (duration: string, day: Date): Date => {
  switch (duration) {
    case 'day':
      return addDays(day, 1)
    case 'week':
      return addDays(day, 7)
    case 'year':
      return addYears(day, 1)
    case 'month':
      return addMonths(day, 1)
    default:
      throw new Error(
        `Invalid duration, expected: "day", "week", "month", "year", got: "${duration}"`
      )
  }
}

export const getDateWithTZ = (dateInUTC: string, tz: string): Date => {
  return toZonedTime(new Date(dateInUTC), tz)
}

export const getCalendarStartAndEnd = (
  date: Date,
  weekStartingMonday: boolean
): Record<string, Date> => {
  const monthStart = startOfMonth(date)
  const monthEnd = endOfMonth(date)
  const weekStartsOn = weekStartingMonday ? 1 : 0
  return {
    start: startOfWeek(monthStart, { weekStartsOn }),
    end: endOfWeek(monthEnd, { weekStartsOn }),
  }
}

export const formatWorkoutDate = (
  dateTime: Date,
  dateFormat: string | null = null
): Record<string, string> => {
  if (!dateFormat) {
    dateFormat = 'yyyy/MM/dd'
  }
  dateFormat = getDateFormat(dateFormat, locale.value)

  return {
    workout_date:
      dateFormat === 'browser_settings'
        ? intlFormat(dateTime)
        : format(dateTime, dateFormat, {
            locale: localeFromLanguage[locale.value],
          }),
    workout_time:
      dateFormat === 'browser_settings'
        ? intlFormat(dateTime, {
            hour: 'numeric',
            minute: 'numeric',
          })
        : format(dateTime, 'HH:mm'),
  }
}

// available formats for user preferences
// for unlogged user, date are displayed with browser settings
const availableDateFormats = [
  'MM/dd/yyyy',
  'dd/MM/yyyy',
  'yyyy-MM-dd',
  'date_string', // depending on language
]
export const dateStringFormats: Record<TLanguage, string> = {
  bg: 'd MMMM yyyy',
  // bn: 'd MMMM, yyyy',
  cs: 'd. MMM yyyy',
  de: 'do MMM yyyy',
  en: 'MMM. do, yyyy',
  es: 'd MMM yyyy',
  eu: 'yyyy MMM. d',
  fr: 'd MMM yyyy',
  gl: 'd MMM yyyy',
  // hr: 'd. MMM yyyy.',
  it: 'd MMM yyyy',
  nb: 'do MMM yyyy',
  nl: 'd MMM yyyy',
  pl: 'd MMM yyyy',
  pt: 'd MMM yyyy',
  ru: 'd MMMM yyyy',
  zh_Hans: 'y年M月d日',
}

export const getDateFormat = (
  dateFormat: string,
  language: TLanguage
): string => {
  return dateFormat === 'date_string'
    ? dateStringFormats[language]
    : dateFormat || 'MM/dd/yyyy'
}

export const formatDate = (
  dateString: string,
  timezone: string,
  dateFormat: string,
  withTime = true,
  language: TLanguage | null = null,
  withSeconds = false
): string => {
  if (!language) {
    language = locale.value
  }

  const dateFormatForLanguage = getDateFormat(dateFormat, language)
  const dateWithTimezone = getDateWithTZ(dateString, timezone)
  if (dateFormatForLanguage === 'browser_settings') {
    let localeOptions: IntlFormatFormatOptions = {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
    }
    if (withTime) {
      localeOptions = {
        ...localeOptions,
        hour: 'numeric',
        minute: 'numeric',
        ...(withSeconds ? { second: 'numeric' } : {}),
      }
    }
    return intlFormat(dateWithTimezone, localeOptions)
  }

  let timeFormat = ''
  if (withTime) {
    timeFormat = withSeconds ? ' HH:mm:ss' : ' HH:mm'
  }
  return format(
    dateWithTimezone,
    `${getDateFormat(dateFormat, language)}${timeFormat}`,
    { locale: localeFromLanguage[language] }
  )
}

export const availableDateFormatOptions = (
  inputDate: string,
  timezone: string,
  language: TLanguage | null = null
) => {
  const l: TLanguage = language ?? locale.value
  const options: Record<string, string>[] = []
  availableDateFormats.forEach((df) => {
    const dateFormat = getDateFormat(df, l)
    options.push({
      label: `${dateFormat} - ${formatDate(
        inputDate,
        timezone,
        dateFormat,
        false,
        l
      )}`,
      value: df,
    })
  })
  return options
}
