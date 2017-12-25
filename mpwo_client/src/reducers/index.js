import { combineReducers } from 'redux'

import initial from './initial'

const message = (state = initial.message, action) => {
  switch (action.type) {
    case 'AUTH_ERROR':
    case 'PROFILE_ERROR':
      return action.message
    case 'LOGOUT':
      return ''
    case 'PROFILE_SUCCESS':
      return ''
    default:
      return state
  }
}

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
        isAuthenticated: true
      }
    default:
      return state
  }
}

const formData = (state = initial.formData, action) => {
  switch (action.type) {
    case 'UPDATE_FORMDATA_EMAIL':
      return {
        formData: {
          ...state.formData,
          email: action.email
        },
      }
    case 'UPDATE_FORMDATA_USERNAME':
      return {
        formData: {
          ...state.formData,
          username: action.username
        },
      }
    case 'UPDATE_FORMDATA_PASSWORD':
      return {
        formData: {
          ...state.formData,
          password: action.password
        },
      }
    case 'PROFILE_SUCCESS':
      return initial.formData
    default:
      return state
  }
}

const reducers = combineReducers({
  message,
  user,
  formData,
})

export default reducers
