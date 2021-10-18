import { format, subHours } from 'date-fns'
import togeojson from '@mapbox/togeojson'

import i18n from '../i18n'
import { getDateWithTZ } from './index'
import { convert } from './conversions'

export const workoutColors = [
  '#55a8a3',
  '#98C3A9',
  '#D0838A',
  '#ECC77E',
  '#926692',
  '#929292',
  '#428bca',
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
    if (i18n.t('km') === 'mi') {
      dateFormat = 'MM/dd/yyyy'
    } else {
      dateFormat = 'yyyy/MM/dd'
    }
  } else {
    if (i18n.t('km') === 'mi') {
      dateFormat = dateFormat.replace('yyyy/MM/dd', 'MM/dd/yyyy')
      dateFormat = dateFormat.replace('dd/MM/yyyy', 'MM/dd/yyyy')
    }
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
    chartData[i].elevation = convert(chartData[i].elevation, i18n.t('common:m'))
    chartData[i].speed = convert(chartData[i].speed, i18n.t('common:km'))
    chartData[i].distance = convert(chartData[i].distance, i18n.t('common:km'))
  }
  return chartData
}

export const formatRecord = (record, tz) => {
  let value
  switch (record.record_type) {
    case 'AS':
    case 'MS':
      value = `${convert(record.value, i18n.t('common:km'))} ${i18n.t(
        'common:km'
      )}/h`
      break
    case 'FD':
      value = `${convert(record.value, i18n.t('common:km'))} ${i18n.t(
        'common:km'
      )}`
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
