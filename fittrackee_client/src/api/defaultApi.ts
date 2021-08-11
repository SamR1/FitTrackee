import axios from 'axios'
import { getApiUrl } from '@/utils'

const api = axios.create({
  baseURL: getApiUrl(),
})

export default api
