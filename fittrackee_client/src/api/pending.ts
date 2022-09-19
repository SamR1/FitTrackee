import { AxiosRequestConfig } from 'axios'

export const pendingRequests = new Map()

const generateRequestKey = (config: AxiosRequestConfig): string => {
  const { method, url, params = {}, data = {} } = config
  return [method, url, JSON.stringify(params), JSON.stringify(data)].join('')
}

export const removeRequestIfPending = (config: AxiosRequestConfig): string => {
  const requestKey = generateRequestKey(config)
  if (pendingRequests.has(requestKey)) {
    const controller = pendingRequests.get(requestKey) || {}
    controller?.abort()
    pendingRequests.delete(requestKey)
  }
  return requestKey
}
