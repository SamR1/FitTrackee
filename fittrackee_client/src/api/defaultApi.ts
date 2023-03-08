import axios from 'axios'

import { pendingRequests, removeRequestIfPending } from '@/api/pending'
import { getApiUrl } from '@/utils'

const api = axios.create({
  baseURL: getApiUrl(),
})

api.interceptors.request.use(
  (config) => {
    const controller = new AbortController()
    config.signal = controller.signal
    const requestKey = removeRequestIfPending(config)
    pendingRequests.set(requestKey, controller)
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => {
    removeRequestIfPending(response.config)
    return response
  },
  (error) => {
    if (error.message !== 'canceled' && error.response) {
      removeRequestIfPending(error.response.config)
    }
    return Promise.reject(error)
  }
)

export default api
