import { format, parse } from 'date-fns'
import { DateTime } from 'luxon'

export const version = '0.2.1-beta' // version stored in 'utils' for now
export const apiUrl = `${process.env.REACT_APP_API_URL}/api/`
export const thunderforestApiKey = `${
  process.env.REACT_APP_THUNDERFOREST_API_KEY
  }`
export const gpxLimit = `${process.env.REACT_APP_GPX_LIMIT_IMPORT}`

export const isLoggedIn = () => !!window.localStorage.authToken

export const generateIds = arr => {
  let i = 0
  return arr.map(val => {
    const obj = { id: i, value: val }
    i++
    return obj
  })
}


export const createApiRequest = params => {
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
  const request = new Request(`${apiUrl}${params.url}`, requestParams)
  return fetch(request)
    .then(response => params.method === 'DELETE'
      ? response
      : response.json())
    .catch(error => {
      console.error(error)
      return new Error('An error occurred. Please contact the administrator.')
    })
}


export const getDateWithTZ = (date, tz) => {
  if (!date) {
    return ''
  }
  const dt = DateTime.fromISO(format(date)).setZone(tz)
  return parse(dt.toFormat('yyyy-MM-dd HH:mm:ss'))
}
