import FitTrackeeGenericApi from '../fitTrackeeApi'
import { history } from '../index'
import { formatChartData } from '../utils/workouts'
import { setError, setLoading } from './index'
import { loadProfile } from './user'

export const pushWorkouts = workouts => ({
  type: 'PUSH_WORKOUTS',
  workouts,
})

export const removeWorkout = workoutId => ({
  type: 'REMOVE_WORKOUT',
  workoutId,
})

export const updateCalendar = workouts => ({
  type: 'UPDATE_CALENDAR',
  workouts,
})

export const setGpx = gpxContent => ({
  type: 'SET_GPX',
  gpxContent,
})

export const setChartData = chartData => ({
  type: 'SET_CHART_DATA',
  chartData,
})

export const addWorkout = form => dispatch =>
  FitTrackeeGenericApi.addDataWithFile('workouts', form)
    .then(ret => {
      if (ret.status === 'created') {
        if (ret.data.workouts.length === 0) {
          dispatch(setError('workouts|no correct file.'))
        } else if (ret.data.workouts.length === 1) {
          dispatch(loadProfile())
          history.push(`/workouts/${ret.data.workouts[0].id}`)
        } else {
          // ret.data.workouts.length > 1
          dispatch(loadProfile())
          history.push('/')
        }
      } else if (ret.status === 413) {
        dispatch(
          setError('workouts|File size is greater than the allowed size')
        )
      } else {
        dispatch(setError(`workouts|${ret.message}`))
      }
      dispatch(setLoading(false))
    })
    .catch(error => {
      dispatch(setLoading(false))
      dispatch(setError(`workouts|${error}`))
    })

export const addWorkoutWithoutGpx = form => dispatch =>
  FitTrackeeGenericApi.addData('workouts/no_gpx', form)
    .then(ret => {
      if (ret.status === 'created') {
        dispatch(loadProfile())
        history.push(`/workouts/${ret.data.workouts[0].id}`)
      } else {
        dispatch(setError(`workouts|${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`workouts|${error}`)))

export const getWorkoutGpx = workoutId => dispatch => {
  if (workoutId) {
    return FitTrackeeGenericApi.getData(`workouts/${workoutId}/gpx`)
      .then(ret => {
        if (ret.status === 'success') {
          dispatch(setGpx(ret.data.gpx))
        } else {
          dispatch(setError(`workouts|${ret.message}`))
        }
      })
      .catch(error => dispatch(setError(`workouts|${error}`)))
  }
  dispatch(setGpx(null))
}

export const getSegmentGpx = (workoutId, segmentId) => dispatch => {
  if (workoutId) {
    return FitTrackeeGenericApi.getData(
      `workouts/${workoutId}/gpx/segment/${segmentId}`
    )
      .then(ret => {
        if (ret.status === 'success') {
          dispatch(setGpx(ret.data.gpx))
        } else {
          dispatch(setError(`workouts|${ret.message}`))
        }
      })
      .catch(error => dispatch(setError(`workouts|${error}`)))
  }
  dispatch(setGpx(null))
}

export const getWorkoutChartData = workoutId => dispatch => {
  if (workoutId) {
    return FitTrackeeGenericApi.getData(`workouts/${workoutId}/chart_data`)
      .then(ret => {
        if (ret.status === 'success') {
          dispatch(setChartData(formatChartData(ret.data.chart_data)))
        } else {
          dispatch(setError(`workouts|${ret.message}`))
        }
      })
      .catch(error => dispatch(setError(`workouts|${error}`)))
  }
  dispatch(setChartData(null))
}

export const getSegmentChartData = (workoutId, segmentId) => dispatch => {
  if (workoutId) {
    return FitTrackeeGenericApi.getData(
      `workouts/${workoutId}/chart_data/segment/${segmentId}`
    )
      .then(ret => {
        if (ret.status === 'success') {
          dispatch(setChartData(formatChartData(ret.data.chart_data)))
        } else {
          dispatch(setError(`workouts|${ret.message}`))
        }
      })
      .catch(error => dispatch(setError(`workouts|${error}`)))
  }
  dispatch(setChartData(null))
}

export const deleteWorkout = id => dispatch =>
  FitTrackeeGenericApi.deleteData('workouts', id)
    .then(ret => {
      if (ret.status === 204) {
        Promise.resolve(dispatch(removeWorkout(id)))
          .then(() => dispatch(loadProfile()))
          .then(() => history.push('/'))
      } else {
        dispatch(setError(`workouts|${ret.status}`))
      }
    })
    .catch(error => dispatch(setError(`workouts|${error}`)))

export const editWorkout = form => dispatch =>
  FitTrackeeGenericApi.updateData('workouts', form)
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(loadProfile())
        history.push(`/workouts/${ret.data.workouts[0].id}`)
      } else {
        dispatch(setError(`workouts|${ret.message}`))
      }
      dispatch(setLoading(false))
    })
    .catch(error => {
      dispatch(setLoading(false))
      dispatch(setError(`workouts|${error}`))
    })

export const getMoreWorkouts = params => dispatch =>
  FitTrackeeGenericApi.getData('workouts', params)
    .then(ret => {
      if (ret.status === 'success') {
        if (ret.data.workouts.length > 0) {
          dispatch(pushWorkouts(ret.data.workouts))
        }
      } else {
        dispatch(setError(`workouts|${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`workouts|${error}`)))

export const getMonthWorkouts = (from, to) => dispatch =>
  FitTrackeeGenericApi.getData('workouts', {
    from,
    to,
    order: 'desc',
    per_page: 100,
  })
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(updateCalendar(ret.data.workouts))
      } else {
        dispatch(setError(`workouts|${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`workouts|${error}`)))
