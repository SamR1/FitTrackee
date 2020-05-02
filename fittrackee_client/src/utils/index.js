import { format, parse } from 'date-fns'
import { DateTime } from 'luxon'

const suffixes = ['bytes', 'KB', 'MB', 'GB', 'TB']
export const getFileSize = (fileSize, asText = true) => {
  const i = Math.floor(Math.log(fileSize) / Math.log(1024))
  if (!fileSize) {
    return asText ? '0 bytes' : { size: 0, suffix: 'bytes' }
  }
  const size = (fileSize / Math.pow(1024, i)).toFixed(1)
  const suffix = suffixes[i]
  return asText ? `${size}${suffix}` : { size, suffix }
}

export const getFileSizeInMB = fileSize => {
  const value = fileSize / 1048576
  return (!fileSize && 0) || +value.toFixed(2)
}

export const version = '0.2.5-beta' // version stored in 'utils' for now
export const apiUrl = `${process.env.REACT_APP_API_URL}/api/`
/* prettier-ignore */
export const thunderforestApiKey = `${
  process.env.REACT_APP_THUNDERFOREST_API_KEY
}`

export const userFilters = [
  { key: 'activities_count', label: 'activities count' },
  { key: 'admin', label: 'admin rights' },
  { key: 'created_at', label: 'registration date' },
  { key: 'username', label: 'user name' },
]

export const sortOrders = [
  { key: 'asc', label: 'ascending' },
  { key: 'desc', label: 'descending' },
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

export const rangePagination = pages =>
  Array.from({ length: pages }, (_, i) => i + 1)

const sortValues = (a, b) => {
  const valueALabel = a.label.toLowerCase()
  const valueBLabel = b.label.toLowerCase()
  return valueALabel > valueBLabel ? 1 : valueALabel < valueBLabel ? -1 : 0
}

export const translateValues = (t, values, key = 'common') =>
  values
    .map(value => ({
      ...value,
      label: t(`${key}:${value.label}`),
    }))
    .sort(sortValues)

export const formatUrl = (pathname, query) => {
  let url = pathname
  if (query.id || (pathname === 'users' && query.username)) {
    url = `${url}/${query.username ? query.username : query.id}`
  } else if (Object.keys(query).length > 0) {
    url += '?'
    Object.keys(query)
      .filter(key => query[key])
      .map(
        (key, index) => (url += `${index === 0 ? '' : '&'}${key}=${query[key]}`)
      )
  }
  return url
}
