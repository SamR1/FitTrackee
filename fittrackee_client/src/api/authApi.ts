import axios from 'axios'

import store from '@/store'
import { USER_STORE } from '@/store/constants'
import { getApiUrl } from '@/utils'

const authApi = axios.create({
  baseURL: getApiUrl(),
})

authApi.interceptors.request.use(
  (config) => {
    const authToken = store.getters[USER_STORE.GETTERS.AUTH_TOKEN]
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
