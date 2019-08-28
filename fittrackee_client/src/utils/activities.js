import { format, subHours } from 'date-fns'
import togeojson from '@mapbox/togeojson'

import { getDateWithTZ } from './index'

export const activityColors = [
  '#55a8a3',
  '#98C3A9',
  '#D0838A',
  '#ECC77E',
  '#926692',
  '#929292',
  '#428bca',
]

export const recordsLabels = [
  { record_type: 'AS', label: 'Avg speed' },
  { record_type: 'FD', label: 'Farest distance' },
  { record_type: 'LD', label: 'Longest duration' },
  { record_type: 'MS', label: 'Max speed' },
]

export const getGeoJson = gpxContent => {
  let jsonData
  if (gpxContent) {
    const gpx = new DOMParser().parseFromString(gpxContent, 'text/xml')
    jsonData = togeojson.gpx(gpx)
  }
  return { jsonData }
}

export const formatActivityDate = (
  dateTime,
  dateFormat = null,
  timeFormat = null
) => {
  if (!dateFormat) {
    dateFormat = 'yyyy/MM/dd'
  }
  if (!timeFormat) {
    timeFormat = 'HH:mm'
  }
  return {
    activity_date: dateTime ? format(dateTime, dateFormat) : null,
    activity_time: dateTime ? format(dateTime, timeFormat) : null,
  }
}

export const formatActivityDuration = seconds => {
  let newDate = new Date(0)
  newDate = subHours(newDate.setSeconds(seconds), 1)
  return newDate.getTime()
}

export const formatChartData = chartData => {
  for (let i = 0; i < chartData.length; i++) {
    chartData[i].time = new Date(chartData[i].time).getTime()
    chartData[i].duration = formatActivityDuration(chartData[i].duration)
  }
  return chartData
}

export const formatRecord = (record, tz) => {
  let value
  switch (record.record_type) {
    case 'AS':
    case 'MS':
      value = `${record.value} km/h`
      break
    case 'FD':
      value = `${record.value} km`
      break
    default:
      // 'LD'
      value = record.value // eslint-disable-line prefer-destructuring
  }
  const [recordType] = recordsLabels.filter(
    r => r.record_type === record.record_type
  )
  return {
    activity_date: formatActivityDate(getDateWithTZ(record.activity_date, tz))
      .activity_date,
    activity_id: record.activity_id,
    id: record.id,
    record_type: recordType.label,
    value: value,
  }
}
