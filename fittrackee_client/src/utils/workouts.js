import { format, subHours } from 'date-fns'
import togeojson from '@mapbox/togeojson'

import { getDateWithTZ } from './index'

export const workoutColors = [
  '#55a8a3', // Cycling (sport)
  '#98C3A9', // Cycling (transport)
  '#D0838A', // Hiking
  '#ECC77E', // Mountain bike
  '#926692', // Running
  '#929292', // Walking
  '#f7af88', // Mountain Biking (Electric)
  '#fbc2a6', // Trail
  '#67a4bd', // Skiing (Alpine)
  '#9498d0', // Skiing (Cross Country)
  '#fad783', // Rowing
]

export const recordsLabels = [
  { record_type: 'AS', label: 'Ave. speed' },
  { record_type: 'FD', label: 'Farest distance' },
  { record_type: 'LD', label: 'Longest duration' },
  { record_type: 'MS', label: 'Max. speed' },
]

export const getGeoJson = gpxContent => {
  let jsonData
  if (gpxContent) {
    const gpx = new DOMParser().parseFromString(gpxContent, 'text/xml')
    jsonData = togeojson.gpx(gpx)
  }
  return { jsonData }
}

export const formatWorkoutDate = (
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
    workout_date: dateTime ? format(dateTime, dateFormat) : null,
    workout_time: dateTime ? format(dateTime, timeFormat) : null,
  }
}

export const formatWorkoutDuration = seconds => {
  let newDate = new Date(0)
  newDate = subHours(newDate.setSeconds(seconds), 1)
  return newDate.getTime()
}

export const formatChartData = chartData => {
  for (let i = 0; i < chartData.length; i++) {
    chartData[i].time = new Date(chartData[i].time).getTime()
    chartData[i].duration = formatWorkoutDuration(chartData[i].duration)
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
    workout_date: formatWorkoutDate(getDateWithTZ(record.workout_date, tz))
      .workout_date,
    workout_id: record.workout_id,
    id: record.id,
    record_type: recordType.label,
    value: value,
  }
}

const sortSports = (a, b) => {
  const sportALabel = a.label.toLowerCase()
  const sportBLabel = b.label.toLowerCase()
  return sportALabel > sportBLabel ? 1 : sportALabel < sportBLabel ? -1 : 0
}

export const translateSports = (sports, t, onlyActive = false) =>
  sports
    .filter(sport => (onlyActive ? sport.is_active : true))
    .map(sport => ({
      ...sport,
      label: t(`sports:${sport.label}`),
    }))
    .sort(sortSports)
