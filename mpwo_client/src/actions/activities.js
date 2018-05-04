import mpwoApi from '../mwpoApi/activities'
import { history } from '../index'
import { setError } from './index'

export const setGpx = gpxContent => ({
  type: 'SET_GPX',
  gpxContent,
})

export function addActivity(form) {
  return function(dispatch) {
    return mpwoApi
    .addActivity(form)
    .then(ret => {
      if (ret.status === 'created') {
        history.push('/')
      } else {
        dispatch(setError(`activities: ${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`activities: ${error}`)))
  }
}

export function getActivityGpx(activityId) {
  if (activityId) {
    return function(dispatch) {
    return mpwoApi
    .getActivityGpx(activityId)
    .then(ret => {
      if (ret.status === 'success') {
         dispatch(setGpx(ret.data.gpx))
      } else {
        dispatch(setError(`activities: ${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`activities: ${error}`)))
    }
  }
  return function(dispatch) {
    dispatch(setGpx(null))
  }
}
