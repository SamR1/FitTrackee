import togeojson from '@mapbox/togeojson'
import bbox from 'geojson-bbox'

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
  let jsonData, bboxCorners
  let bounds = [[0, 0], [0, 0]]
  if (gpxContent) {
    const gpx = new DOMParser().parseFromString(gpxContent, 'text/xml')
    jsonData = togeojson.gpx(gpx)
    bboxCorners = bbox(jsonData)
      bounds = [
      [bboxCorners[1], bboxCorners[0]],
      [bboxCorners[3], bboxCorners[2]]
    ]
  }
  return { jsonData, bounds }
}
