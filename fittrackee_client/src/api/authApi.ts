import axios from 'axios'

import { pendingRequests, removeRequestIfPending } from '@/api/pending'
import store from '@/store'
import { AUTH_USER_STORE } from '@/store/constants'
import { getApiUrl } from '@/utils'

const authApi = axios.create({
  baseURL: getApiUrl(),
})

authApi.interceptors.request.use(
  (config) => {
    const controller = new AbortController()
    config.signal = controller.signal
    const requestKey = removeRequestIfPending(config)
    pendingRequests.set(requestKey, controller)

    const authToken = store.getters[AUTH_USER_STORE.GETTERS.AUTH_TOKEN]
    if (authToken) {
      const auth = `Bearer ${authToken}`
      if (config.headers && config.headers.Authorization !== auth) {
        config.headers.Authorization = `Bearer ${authToken}`
      }
    }
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
