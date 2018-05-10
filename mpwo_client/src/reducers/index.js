import { format } from 'date-fns'
import { routerReducer } from 'react-router-redux'
import { combineReducers } from 'redux'

import initial from './initial'

const handleDataAndError = (state, type, action) => {
  if (action.target !== type) {
    return state
  }
  switch (action.type) {
    case 'SET_DATA':
      return {
        ...state,
        data: action.data[action.target],
      }
    default:
      return state
  }
}

const activities = (state = initial.activities, action) => {
  switch (action.type) {
    case 'END_PAGINATION':
      return {
        ...state,
        pagination_end: true
      }
    case 'PUSH_ACTIVITIES':
      return {
        ...state,
        data: state.data.concat(action.activities),
      }
    default:
      return handleDataAndError(state, 'activities', action)
  }
}

const formData = (state = initial.formData, action) => {
  switch (action.type) {
    case 'UPDATE_USER_FORMDATA':
      return {
        formData: {
          ...state.formData,
          [action.target]: action.value
        },
      }
    case 'PROFILE_SUCCESS':
    case 'EMPTY_USER_FORMDATA':
      return initial.formData
    default:
      return state
  }
}

const formProfile = (state = initial.formProfile, action) => {
  switch (action.type) {
    case 'UPDATE_PROFILE_FORMDATA':
      return {
        formProfile: {
          ...state.formProfile,
          [action.target]: action.value
        },
      }
    case 'INIT_PROFILE_FORM':
      return {
        formProfile: {
          ...state.formProfile,
          firstName: action.user.firstName,
          lastName: action.user.lastName,
          birthDate: action.user.birthDate,
          location: action.user.location,
          bio: action.user.bio,
        },
      }
    case 'PROFILE_SUCCESS':
      return initial.formProfile
    default:
      return state
  }
}

const gpx = (state = initial.gpx, action) => {
  switch (action.type) {
    case 'SET_GPX':
      return action.gpxContent
    default:
      return state
  }
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
      return {
        id: action.message.data.id,
        username: action.message.data.username,
        email: action.message.data.email,
        isAdmin: action.message.data.admin,
        createdAt: action.message.data.created_at,
        isAuthenticated: true,
        firstName: action.message.data.first_name
                   ? action.message.data.first_name
                   : '',
        lastName: action.message.data.last_name
                   ? action.message.data.last_name
                   : '',
        bio: action.message.data.bio
                   ? action.message.data.bio
                   : '',
        location: action.message.data.location
                   ? action.message.data.location
                   : '',
        birthDate: action.message.data.birth_date
                   ? format(new Date(action.message.data.birth_date),
                            'DD/MM/YYYY')
                   : '',
        picture: action.message.data.picture === true
                   ? action.message.data.picture
                   : false,
      }
    default:
      return state
  }
}

const reducers = combineReducers({
  activities,
  formData,
  formProfile,
  gpx,
  message,
  messages,
  router: routerReducer,
  sports,
  user,
})

export default reducers
