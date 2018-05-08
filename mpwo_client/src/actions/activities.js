import mpwoApi from '../mwpoApi/activities'
import { history } from '../index'
import { setError } from './index'

export const setGpx = gpxContent => ({
  type: 'SET_GPX',
  gpxContent,
})

export const addActivity = form => dispatch => mpwoApi
  .addActivity(form)
  .then(ret => {
    if (ret.status === 'created') {
      history.push('/')
    } else {
      dispatch(setError(`activities: ${ret.message}`))
    }
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))


export const addActivityWithoutGpx = form => dispatch => mpwoApi
  .addActivityWithoutGpx(form)
  .then(ret => {
    if (ret.status === 'created') {
      history.push('/')
    } else {
      dispatch(setError(`activities: ${ret.message}`))
    }
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))


export const getActivityGpx = activityId => dispatch => {
  if (activityId) {
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
  dispatch(setGpx(null))
}
