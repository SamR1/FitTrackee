import { connectRouter } from 'connected-react-router'
import { combineReducers } from 'redux'

import initial from './initial'

const handleDataAndError = (state, type, action) => {
  if (action.target !== type) {
    return state
  }
  if (action.type === 'SET_DATA') {
    return {
      ...state,
      data: action.data[action.target],
    }
  }
  return state
}

const activities = (state = initial.activities, action) => {
  switch (action.type) {
    case 'PUSH_ACTIVITIES':
      return {
        ...state,
        data: state.data.concat(action.activities),
      }
    case 'REMOVE_ACTIVITY':
      return {
        ...state,
        data: state.data.filter(activity => activity.id !== action.activityId),
      }
    default:
      return handleDataAndError(state, 'activities', action)
  }
}

const calendarActivities = (state = initial.calendarActivities, action) => {
  if (action.type === 'UPDATE_CALENDAR') {
    return {
      ...state,
      data: action.activities,
    }
  }
  return handleDataAndError(state, 'calendarActivities', action)
}

const chartData = (state = initial.chartData, action) => {
  if (action.type === 'SET_CHART_DATA') {
    return action.chartData
  }
  return state
}

const gpx = (state = initial.gpx, action) => {
  if (action.type === 'SET_GPX') {
    return action.gpxContent
  }
  return state
}

const language = (state = initial.language, action) => {
  if (action.type === 'SET_LANGUAGE') {
    return action.language
  }
  return state
}

const loading = (state = initial.loading, action) => {
  if (action.type === 'SET_LOADING') {
    return action.loading
  }
  return state
}

const message = (state = initial.message, action) => {
  switch (action.type) {
    case 'AUTH_ERROR':
    case 'PROFILE_ERROR':
    case 'PROFILE_UPDATE_ERROR':
    case 'PICTURE_ERROR':
    case 'SET_ERROR':
      return action.message
    case 'LOGOUT':
    case 'PROFILE_SUCCESS':
    case 'SET_RESULTS':
    case '@@router/LOCATION_CHANGE':
      return ''
    default:
      return state
  }
}

const messages = (state = initial.messages, action) => {
  switch (action.type) {
    case 'AUTH_ERRORS':
      return action.messages
    case 'LOGOUT':
    case 'PROFILE_SUCCESS':
    case '@@router/LOCATION_CHANGE':
      return []
    default:
      return state
  }
}

const records = (state = initial.records, action) =>
  handleDataAndError(state, 'records', action)

const sports = (state = initial.sports, action) =>
  handleDataAndError(state, 'sports', action)

const user = (state = initial.user, action) => {
  switch (action.type) {
    case 'AUTH_ERROR':
    case 'PROFILE_ERROR':
    case 'LOGOUT':
      window.localStorage.removeItem('authToken')
      return initial.user
    case 'PROFILE_SUCCESS':
      return action.profil
    default:
      return state
  }
}

const statistics = (state = initial.statistics, action) =>
  handleDataAndError(state, 'statistics', action)

export default history =>
  combineReducers({
    activities,
    calendarActivities,
    chartData,
    gpx,
    language,
    loading,
    message,
    messages,
    records,
    router: connectRouter(history),
    sports,
    statistics,
    user,
  })
