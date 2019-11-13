import { format, parse } from 'date-fns'
import { DateTime } from 'luxon'

const suffixes = ['bytes', 'KB', 'MB', 'GB', 'TB']
export const getFileSize = fileSize => {
  const i = Math.floor(Math.log(fileSize) / Math.log(1024))
  return (
    (!fileSize && '0 bytes') ||
    `${(fileSize / Math.pow(1024, i)).toFixed(1)}${suffixes[i]}`
  )
}

export const getFileSizeInMB = fileSize => {
  const value = fileSize / 1048576
  return (!fileSize && 0) || +value.toFixed(2)
}

export const version = '0.3.0-beta' // version stored in 'utils' for now
export const apiUrl = `${process.env.REACT_APP_API_URL}/api/`
/* prettier-ignore */
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

export const createApiRequest = params => {
  const headers = {}
  if (!params.noAuthorization) {
    headers.Authorization = `Bearer ${window.localStorage.getItem('authToken')}`
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
    .then(response =>
      params.method === 'DELETE' || response.status === 413
        ? response
        : response.json()
    )
    .catch(error => {
      console.error(error)
      return new Error('An error occurred. Please contact the administrator.')
    })
}

export const getDateWithTZ = (date, tz) => {
  if (!date) {
    return ''
  }
  const dt = DateTime.fromISO(
    format(new Date(date), "yyyy-MM-dd'T'HH:mm:ss.SSSxxx")
  ).setZone(tz)
  return parse(
    dt.toFormat('yyyy-MM-dd HH:mm:ss'),
    'yyyy-MM-dd HH:mm:ss',
    new Date()
  )
}

export const capitalize = target =>
  target.charAt(0).toUpperCase() + target.slice(1)
