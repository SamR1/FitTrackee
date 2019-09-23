import FitTrackeeGenericApi from '../fitTrackeeApi'
import { setData, setError } from './index'

export const setAppStats = data => ({
  type: 'SET_APP_STATS',
  data,
})

export const getAppStats = () => dispatch =>
  FitTrackeeGenericApi.getData('stats/all')
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(setAppStats(ret.data))
      } else {
        dispatch(setError(`application|${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`application|${error}`)))

export const getStats = (userId, type, data) => dispatch =>
  FitTrackeeGenericApi.getData(`stats/${userId}/${type}`, data)
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(setData('statistics', ret.data))
      } else {
        dispatch(setError(`statistics|${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`statistics|${error}`)))
