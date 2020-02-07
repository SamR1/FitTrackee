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
    case 'LOGOUT':
      return initial.activities
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

const application = (state = initial.application, action) => {
  if (action.type === 'SET_APP_CONFIG') {
    return {
      ...state,
      config: action.data,
    }
  }
  if (action.type === 'SET_APP_STATS') {
    return {
      ...state,
      statistics: action.data,
    }
  }
  return state
}

const calendarActivities = (state = initial.calendarActivities, action) => {
  switch (action.type) {
    case 'LOGOUT':
      return initial.calendarActivities
    case 'UPDATE_CALENDAR':
      return {
        ...state,
        data: action.activities,
      }
    default:
      return handleDataAndError(state, 'calendarActivities', action)
  }
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

const records = (state = initial.records, action) => {
  if (action.type === 'LOGOUT') {
    return initial.records
  }
  return handleDataAndError(state, 'records', action)
}

const sports = (state = initial.sports, action) => {
  if (action.type === 'UPDATE_SPORT_DATA') {
    return {
      ...state,
      data: state.data.map(sport => {
        if (sport.id === action.data.id) {
          sport.is_active = action.data.is_active
        }
        return sport
      }),
    }
  }
  return handleDataAndError(state, 'sports', action)
}

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

const statistics = (state = initial.statistics, action) => {
  if (action.type === 'LOGOUT') {
    return initial.statistics
  }
  return handleDataAndError(state, 'statistics', action)
}

const users = (state = initial.users, action) =>
  handleDataAndError(state, 'users', action)

export default history =>
  combineReducers({
    activities,
    application,
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
    users,
  })
