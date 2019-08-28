import {
  addDays,
  addMonths,
  addYears,
  format,
  startOfMonth,
  startOfWeek,
  startOfYear,
} from 'date-fns'

const xAxisFormats = [
  { duration: 'week', dateFormat: 'yyyy-MM-dd', xAxis: 'dd/MM' },
  { duration: 'month', dateFormat: 'yyyy-MM', xAxis: 'MM/yyyy' },
  { duration: 'year', dateFormat: 'yyyy', xAxis: 'yyyy' },
]

export const formatDuration = (totalSeconds, formatWithDay = false) => {
  let days = '0'
  if (formatWithDay) {
    days = String(Math.floor(totalSeconds / 86400))
    totalSeconds %= 86400
  }
  const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, '0')
  totalSeconds %= 3600
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0')
  const seconds = String(totalSeconds % 60).padStart(2, '0')
  if (formatWithDay) {
    return `${days === '0' ? '' : `${days}d:`}${
      hours === '00' ? '' : `${hours}h:`
    }${minutes}m:${seconds}s`
  }
  return `${hours === '00' ? '' : `${hours}:`}${minutes}:${seconds}`
}

export const formatValue = (displayedData, value) =>
  value === 0
    ? ''
    : displayedData === 'distance'
    ? `${value.toFixed(2)} km`
    : displayedData === 'duration'
    ? formatDuration(value)
    : value

const dateIncrement = (duration, day) => {
  switch (duration) {
    case 'week':
      return addDays(day, 7)
    case 'year':
      return addYears(day, 1)
    case 'month':
    default:
      return addMonths(day, 1)
  }
}

const startDate = (duration, day) => {
  switch (duration) {
    case 'week':
      return startOfWeek(day)
    case 'year':
      return startOfYear(day)
    case 'month':
    default:
      return startOfMonth(day)
  }
}

export const formatStats = (stats, sports, params, displayedSports) => {
  const nbActivitiesStats = []
  const distanceStats = []
  const durationStats = []

  for (
    let day = startDate(params.duration, params.start);
    day <= params.end;
    day = dateIncrement(params.duration, day)
  ) {
    const [xAxisFormat] = xAxisFormats.filter(
      x => x.duration === params.duration
    )
    const date = format(day, xAxisFormat.dateFormat)
    const xAxis = format(day, xAxisFormat.xAxis)
    const dataNbActivities = { date: xAxis }
    const dataDistance = { date: xAxis }
    const dataDuration = { date: xAxis }

    if (stats[date]) {
      Object.keys(stats[date])
        .filter(sportId =>
          displayedSports ? displayedSports.includes(+sportId) : true
        )
        .map(sportId => {
          const sportLabel = sports.filter(s => s.id === +sportId)[0].label
          dataNbActivities[sportLabel] = stats[date][sportId].nb_activities
          dataDistance[sportLabel] = stats[date][sportId].total_distance
          dataDuration[sportLabel] = stats[date][sportId].total_duration
          return null
        })
    }
    nbActivitiesStats.push(dataNbActivities)
    distanceStats.push(dataDistance)
    durationStats.push(dataDuration)
  }

  return {
    activities: nbActivitiesStats,
    distance: distanceStats,
    duration: durationStats,
  }
}
