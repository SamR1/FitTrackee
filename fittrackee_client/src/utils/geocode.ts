import authApi from '@/api/authApi.ts'
import type { ILocation } from '@/types/workouts.ts'

export const getLocationFromQuery = async (
  query: string
): Promise<ILocation[]> => {
  return await authApi
    .get('/geocode/search', { params: { query } })
    .then((res) => {
      if (res.data.status === 'success') {
        return res.data.locations
      }
      return []
    })
    .catch((error) => {
      console.error(error)
      return []
    })
}
