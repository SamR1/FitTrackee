import {
  addDays,
  addMonths,
  addYears,
  endOfMonth,
  endOfWeek,
  format,
  startOfMonth,
  startOfWeek,
  startOfYear,
} from 'date-fns'
import { utcToZonedTime } from 'date-fns-tz'

export const getStartDate = (
  duration: string,
  day: Date,
  weekStartingMonday: boolean
): Date => {
  switch (duration) {
    case 'week':
      return startOfWeek(day, { weekStartsOn: weekStartingMonday ? 1 : 0 })
    case 'year':
      return startOfYear(day)
    case 'month':
      return startOfMonth(day)
    default:
      throw new Error(
        `Invalid duration, expected: "week", "month", "year", got: "${duration}"`
      )
  }
}

export const incrementDate = (duration: string, day: Date): Date => {
  switch (duration) {
    case 'week':
      return addDays(day, 7)
    case 'year':
      return addYears(day, 1)
    case 'month':
      return addMonths(day, 1)
    default:
      throw new Error(
        `Invalid duration, expected: "week", "month", "year", got: "${duration}"`
      )
  }
}

export const getDateWithTZ = (dateInUTC: string, tz: string): Date => {
  return utcToZonedTime(new Date(dateInUTC), tz)
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
  dateFormat: string | null = null,
  timeFormat: string | null = null
): Record<string, string> => {
  if (!dateFormat) {
    dateFormat = 'yyyy/MM/dd'
  }
  if (!timeFormat) {
    timeFormat = 'HH:mm'
  }
  return {
    workout_date: format(dateTime, dateFormat),
    workout_time: format(dateTime, timeFormat),
  }
}

export const formatDate = (
  dateString: string,
  timezone: string,
  dateFormat: string,
  withTime = true
): string =>
  format(
    getDateWithTZ(dateString, timezone),
    `${dateFormat}${withTime ? ' HH:mm' : ''}`
  )
