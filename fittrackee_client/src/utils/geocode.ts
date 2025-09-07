import authApi from '@/api/authApi.ts'
import type { ILocation } from '@/types/workouts.ts'

export const getLocationFromCity = async (
  city: string
): Promise<ILocation[]> => {
  return await authApi
    .get('/geocode/search', { params: { city } })
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

export const getLocationFromOsmId = async (
  osmId: string
): Promise<ILocation> => {
  return await authApi
    .get('/geocode/lookup', { params: { osm_id: osmId } })
    .then((res) => {
      if (res.data.status === 'success') {
        return res.data.location
      }
      return {}
    })
    .catch((error) => {
      console.error(error)
      return {}
    })
}
