import axios from 'axios'

import store from '@/store'
import { AUTH_USER_STORE } from '@/store/constants'
import { getApiUrl } from '@/utils'

const authApi = axios.create({
  baseURL: getApiUrl(),
})

authApi.interceptors.request.use(
  (config) => {
    const authToken = store.getters[AUTH_USER_STORE.GETTERS.AUTH_TOKEN]
    if (authToken) {
      const auth = `Bearer ${authToken}`
      if (config.headers.Authorization !== auth) {
        config.headers.Authorization = `Bearer ${authToken}`
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default authApi
