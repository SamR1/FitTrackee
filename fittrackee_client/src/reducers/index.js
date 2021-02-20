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
  if (action.type === 'SET_PAGINATED_DATA') {
    return {
      ...state,
      data: action.data[action.target],
      pagination: action.pagination,
    }
  }
  return state
}

const workouts = (state = initial.workouts, action) => {
  switch (action.type) {
    case 'LOGOUT':
      return initial.workouts
    case 'PUSH_WORKOUTS':
      return {
        ...state,
        data: state.data.concat(action.workouts),
      }
    case 'REMOVE_WORKOUT':
      return {
        ...state,
        data: state.data.filter(workout => workout.id !== action.workoutId),
      }
    default:
      return handleDataAndError(state, 'workouts', action)
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

const calendarWorkouts = (state = initial.calendarWorkouts, action) => {
  switch (action.type) {
    case 'LOGOUT':
      return initial.calendarWorkouts
    case 'UPDATE_CALENDAR':
      return {
        ...state,
        data: action.workouts,
      }
    default:
      return handleDataAndError(state, 'calendarWorkouts', action)
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
    case 'CLEAN_ALL_MESSAGES':
    case 'LOGOUT':
    case 'PROFILE_SUCCESS':
    case 'SET_APP_CONFIG':
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
    case 'APP_ERRORS':
      return action.messages
    case 'CLEAN_ALL_MESSAGES':
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

const users = (state = initial.users, action) => {
  if (action.type === 'UPDATE_USER_DATA') {
    return {
      ...state,
      data: state.data.map(user => {
        if (user.username === action.data.username) {
          user.admin = action.data.admin
        }
        return user
      }),
    }
  }
  return handleDataAndError(state, 'users', action)
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

export default history =>
  combineReducers({
    workouts,
    application,
    calendarWorkouts,
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
