import axios from 'axios'

import { pendingRequests, removeRequestIfPending } from '@/api/pending'
import { getCookieValue } from '@/utils/cookies'

const authApi = axios.create({
  baseURL: '/api/',
  withCredentials: true,
})

authApi.interceptors.request.use(
  (config) => {
    const controller = new AbortController()
    config.signal = controller.signal
    const requestKey = removeRequestIfPending(config)
    pendingRequests.set(requestKey, controller)
    config.headers['X-CSRF-TOKEN'] = getCookieValue()
    return config
  },
  (error) => Promise.reject(error)
)

authApi.interceptors.response.use(
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

export default authApi
