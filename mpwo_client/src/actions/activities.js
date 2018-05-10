import mpwoGenericApi from '../mwpoApi'
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
      history.push(`/activities/${ret.data.activities[0].id}`)
    } else {
      dispatch(setError(`activities: ${ret.message}`))
    }
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))


export const addActivityWithoutGpx = form => dispatch => mpwoApi
  .addActivityWithoutGpx(form)
  .then(ret => {
    if (ret.status === 'created') {
      history.push(`/activities/${ret.data.activities[0].id}`)
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


export const deleteActivity = id => dispatch => mpwoGenericApi
  .deleteData('activities', id)
  .then(ret => {
    if (ret.status === 204) {
      history.push('/')
    }
      dispatch(setError(`activities: ${ret.status}`))
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))


export const editActivity = form => dispatch => mpwoGenericApi
  .updateData('activities', form)
  .then(ret => {
    if (ret.status === 'success') {
      history.push(`/activities/${ret.data.activities[0].id}`)
    } else {
      dispatch(setError(`activities: ${ret.message}`))
    }
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))
