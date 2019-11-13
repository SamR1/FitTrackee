import FitTrackeeGenericApi from '../fitTrackeeApi'
import { setError } from './index'

export const setAppConfig = data => ({
  type: 'SET_APP_CONFIG',
  data,
})

export const setAppStats = data => ({
  type: 'SET_APP_STATS',
  data,
})

export const getAppData = target => dispatch =>
  FitTrackeeGenericApi.getData(target)
    .then(ret => {
      if (ret.status === 'success') {
        if (target === 'config') {
          dispatch(setAppConfig(ret.data))
        } else if (target === 'stats/all') {
          dispatch(setAppStats(ret.data))
        }
      } else {
        dispatch(setError(`application|${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`application|${error}`)))

export const updateAppConfig = formData => dispatch =>
  FitTrackeeGenericApi.updateData('config', formData)
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(setAppConfig(ret.data))
      } else {
        dispatch(setError(`application|${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`application|${error}`)))
