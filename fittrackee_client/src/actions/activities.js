import { parse } from 'date-fns'

import FitTrackeeGenericApi from '../fitTrackeeApi'
import { history } from '../index'
import { formatChartData } from '../utils/stats'
import { setError, setLoading } from './index'
import { loadProfile } from './user'

export const pushActivities = activities => ({
  type: 'PUSH_ACTIVITIES',
  activities,
})

export const updateCalendar = activities => ({
  type: 'UPDATE_CALENDAR',
  activities,
})

export const setGpx = gpxContent => ({
  type: 'SET_GPX',
  gpxContent,
})

export const setChartData = chartData => ({
  type: 'SET_CHART_DATA',
  chartData,
})

export const addActivity = form => dispatch => FitTrackeeGenericApi
  .addDataWithFile('activities', form)
  .then(ret => {
    if (ret.status === 'created') {
      if (ret.data.activities.length === 0) {
          dispatch(setError('activities: no correct file'))
      } else if (ret.data.activities.length === 1) {
          dispatch(loadProfile())
          history.push(`/activities/${ret.data.activities[0].id}`)
      } else { // ret.data.activities.length > 1
          dispatch(loadProfile())
          history.push('/')
      }
    } else {
      dispatch(setError(`activities: ${ret.message}`))
    }
    dispatch(setLoading(false))
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))


export const addActivityWithoutGpx = form => dispatch => FitTrackeeGenericApi
  .addData('activities/no_gpx', form)
  .then(ret => {
    if (ret.status === 'created') {
      dispatch(loadProfile())
      history.push(`/activities/${ret.data.activities[0].id}`)
    } else {
      dispatch(setError(`activities: ${ret.message}`))
    }
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))


export const getActivityGpx = activityId => dispatch => {
  if (activityId) {
    return FitTrackeeGenericApi
    .getData(`activities/${activityId}/gpx`)
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


export const getActivityChartData = activityId => dispatch => {
  if (activityId) {
    return FitTrackeeGenericApi
    .getData(`activities/${activityId}/chart_data`)
    .then(ret => {
      if (ret.status === 'success') {
         dispatch(setChartData(formatChartData(ret.data.chart_data)))
      } else {
        dispatch(setError(`activities: ${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`activities: ${error}`)))
  }
  dispatch(setChartData(null))
}


export const deleteActivity = id => dispatch => FitTrackeeGenericApi
  .deleteData('activities', id)
  .then(ret => {
    if (ret.status === 204) {
      dispatch(loadProfile())
      history.push('/')
    } else {
      dispatch(setError(`activities: ${ret.status}`))
    }
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))


export const editActivity = form => dispatch => FitTrackeeGenericApi
  .updateData('activities', form)
  .then(ret => {
    if (ret.status === 'success') {
      dispatch(loadProfile())
      history.push(`/activities/${ret.data.activities[0].id}`)
    } else {
      dispatch(setError(`activities: ${ret.message}`))
    }
    dispatch(setLoading(false))
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))


export const getMoreActivities = params => dispatch => FitTrackeeGenericApi
  .getData('activities', params)
  .then(ret => {
    if (ret.status === 'success') {
      if (ret.data.activities.length > 0) {
        dispatch(pushActivities(ret.data.activities))
      }
    } else {
      dispatch(setError(`activities: ${ret.message}`))
    }
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))

export const getMonthActivities = (from, to) => dispatch =>
  FitTrackeeGenericApi
  .getData('activities', { from, to, order: 'asc', per_page: 100 })
  .then(ret => {
    if (ret.status === 'success') {
      if (ret.data.activities.length > 0) {
        for (let i = 0; i < ret.data.activities.length; i++) {
          ret.data.activities[i].activity_date = parse(
            ret.data.activities[i].activity_date
          )
        }
      }
      dispatch(updateCalendar(ret.data.activities))
    } else {
      dispatch(setError(`activities: ${ret.message}`))
    }
  })
  .catch(error => dispatch(setError(`activities: ${error}`)))
