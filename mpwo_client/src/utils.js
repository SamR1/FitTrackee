import togeojson from '@mapbox/togeojson'
import { format, parse } from 'date-fns'

export const apiUrl = `${process.env.REACT_APP_API_URL}/api/`
export const thunderforestApiKey = `${
  process.env.REACT_APP_THUNDERFOREST_API_KEY
}`

export const isLoggedIn = () => !!window.localStorage.authToken

export const generateIds = arr => {
  let i = 0
  return arr.map(val => {
        const obj = { id: i, value: val }
        i++
        return obj
    })
}

export const getGeoJson = gpxContent => {
  let jsonData
  if (gpxContent) {
    const gpx = new DOMParser().parseFromString(gpxContent, 'text/xml')
    jsonData = togeojson.gpx(gpx)
  }
  return { jsonData }
}

export const formatActivityDate = activityDateTime => {
  if (activityDateTime) {
    const dateTime = parse(activityDateTime)
    return {
      activity_date: format(dateTime, 'YYYY-MM-DD'),
      activity_time: activityDateTime.match(/[0-2][0-9]:[0-5][0-9]/)[0]
    }
  }
  return {
    activity_date: null,
    activity_time: null,
  }
}
