import togeojson from '@mapbox/togeojson'
import {
  addDays, addMonths, addYears, format, parse, startOfWeek
} from 'date-fns'
import { DateTime } from 'luxon'

export const apiUrl = `${process.env.REACT_APP_API_URL}/api/`
export const thunderforestApiKey = `${
  process.env.REACT_APP_THUNDERFOREST_API_KEY
  }`
export const gpxLimit = `${process.env.REACT_APP_GPX_LIMIT_IMPORT}`
export const activityColors = [
  '#55a8a3',
  '#98C3A9',
  '#D0838A',
  '#ECC77E',
  '#926692',
  '#929292',
  '#428bca',
]

export const isLoggedIn = () => !!window.localStorage.authToken

export const generateIds = arr => {
  let i = 0
  return arr.map(val => {
    const obj = { id: i, value: val }
    i++
    return obj
  })
}


export const createRequest = params => {
  const headers = {}
  if (!params.noAuthorization) {
    headers.Authorization = `Bearer ${
      window.localStorage.getItem('authToken')}`
  }
  if (params.type) {
    headers['Content-Type'] = params.type
  }
  const requestParams = {
    method: params.method,
    headers: headers,
  }
  if (params.type === 'application/json' && params.body) {
    requestParams.body = JSON.stringify(params.body)
  } else if (params.body) {
    requestParams.body = params.body
  }
  const request = new Request(params.url, requestParams)
  return fetch(request)
    .then(response => params.method === 'DELETE'
      ? response
      : response.json())
    .catch(error => error)
}


export const getGeoJson = gpxContent => {
  let jsonData
  if (gpxContent) {
    const gpx = new DOMParser().parseFromString(gpxContent, 'text/xml')
    jsonData = togeojson.gpx(gpx)
  }
  return { jsonData }
}


export const getDateWithTZ = (date, tz) => {
  if (!date) {
    return ''
  }
  const dt = DateTime.fromISO(format(date)).setZone(tz)
  return parse(dt.toFormat('yyyy-MM-dd HH:mm:ss'))
}

export const formatActivityDate = (
  dateTime,
  dateFormat = null,
  timeFormat = null,
) => {
  if (!dateFormat) {
    dateFormat = 'DD/MM/YYYY'
  }
  if (!timeFormat) {
    timeFormat = 'HH:mm'
  }
  return {
    activity_date: dateTime ? format(dateTime, dateFormat) : null,
    activity_time: dateTime ? format(dateTime, timeFormat) : null,
  }
}

export const recordsLabels = [
  { record_type: 'AS', label: 'Avg speed' },
  { record_type: 'FD', label: 'Farest distance' },
  { record_type: 'LD', label: 'Longest duration' },
  { record_type: 'MS', label: 'Max speed' },
]

export const formatRecord = (record, tz) => {
  let value, recordType = null
  switch (record.record_type) {
    case 'AS':
    case 'MS':
      value = `${record.value} km/h`
      break
    case 'FD':
      value = `${record.value} km`
      break
    default: // 'LD'
      value = record.value // eslint-disable-line prefer-destructuring
  }
  [recordType] = recordsLabels.filter(r => r.record_type === record.record_type)
  return {
    activity_date: formatActivityDate(
      getDateWithTZ(record.activity_date, tz)
    ).activity_date,
    activity_id: record.activity_id,
    id: record.id,
    record_type: recordType.label,
    value: value,
  }
}

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
    return `${
      days === '0' ? '' : `${days}d:`
    }${
      hours === '00' ? '' : `${hours}h:`
    }${minutes}m:${seconds}s`
  }
  return `${hours === '00' ? '' : `${hours}:`}${minutes}:${seconds}`
}

export const formatChartData = chartData => {
  for (let i = 0; i < chartData.length; i++) {
    chartData[i].time = new Date(chartData[i].time).getTime()
    chartData[i].duration = formatDuration(chartData[i].duration)
  }
  return chartData
}

const xAxisFormats = [
  { duration: 'week', dateFormat: 'YYYY-MM-DD', xAxis: 'DD/MM' },
  { duration: 'month', dateFormat: 'YYYY-MM', xAxis: 'MM/YYYY' },
  { duration: 'year', dateFormat: 'YYYY', xAxis: 'YYYY' },
]

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

export const formatStats = (
  stats, sports, params
) => {
  const nbActivitiesStats = []
  const distanceStats = []
  const durationStats = []

  for (let day = startOfWeek(params.start);
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
      Object.keys(stats[date]).map(sportId => {
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
    duration: durationStats
  }
}
