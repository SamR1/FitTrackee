import {
  addDays,
  addMonths,
  addYears,
  startOfMonth,
  startOfWeek,
  startOfYear,
} from 'date-fns'

export const startDate = (
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
