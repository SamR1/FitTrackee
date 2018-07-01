import togeojson from '@mapbox/togeojson'
import { addDays, format, parse, startOfWeek, subHours } from 'date-fns'
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

export const formatRecord = (record, tz) => {
  let value, recordType = null
  switch (record.record_type) {
    case 'AS':
    case 'MS':
      value = `${record.value} km/h`
      recordType = record.record_type === 'AS' ? 'Avg speed' : 'Max speed'
      break
    case 'FD':
      value = `${record.value} km`
      recordType = 'Farest distance'
      break
    default: // 'LD'
      value = record.value // eslint-disable-line prefer-destructuring
      recordType = 'Longest duration'
  }
  return {
    activity_date: formatActivityDate(
      getDateWithTZ(record.activity_date, tz)
    ).activity_date,
    activity_id: record.activity_id,
    id: record.id,
    record_type: recordType,
    value: value,
  }
}

export const formatDuration = seconds => {
    let newDate = new Date(0)
    newDate = subHours(newDate.setSeconds(seconds), 1)
    return newDate.getTime()
}

export const formatChartData = chartData => {
  for (let i = 0; i < chartData.length; i++) {
    chartData[i].time = new Date(chartData[i].time).getTime()
    chartData[i].duration = formatDuration(chartData[i].duration)
  }
  return chartData
}

export const formatStats = (stats, sports, startDate, endDate) => {
  const nbActivitiesStats = []
  const distanceStats = []
  const durationStats = []

  for (let day = startOfWeek(startDate);
       day <= endDate;
       day = addDays(day, 7)
  ) {
    const date = format(day, 'YYYY-MM-DD')
    const xAxis = format(day, 'DD/MM')
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
