import mpwoApi from '../mpwoApi'

function AuthError(message) {
  return { type: 'AUTH_ERROR', message }
}

function ProfileSuccess(message) {
  return { type: 'PROFILE_SUCCESS', message }
}

function ProfileError(message) {
  return { type: 'PROFILE_ERROR', message }
}

const updateFormDataEmail = value => ({
  type: 'UPDATE_FORMDATA_EMAIL',
  email: value,
})

const updateFormDataUsername = value => ({
  type: 'UPDATE_FORMDATA_USERNAME',
  username: value,
})

const updateFormDataPassword = value => ({
  type: 'UPDATE_FORMDATA_PASSWORD',
  password: value,
})

export function getProfile(dispatch) {
  return mpwoApi
    .getProfile()
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(ProfileSuccess(ret))
      } else {
        dispatch(ProfileError(ret.message))
      }
    })
    .catch(error => {
      throw error
    })
}

export function register(formData) {
  return function(dispatch) {
    return mpwoApi
      .register(formData.username, formData.email, formData.password)
      .then(ret => {
        if (ret.status === 'success') {
          window.localStorage.setItem('authToken', ret.auth_token)
          getProfile(dispatch)
        } else {
          dispatch(AuthError(ret.message))
        }
      })
      .catch(error => {
        throw error
      })
  }
}

export function login(formData) {
  return function(dispatch) {
    return mpwoApi
      .login(formData.email, formData.password)
      .then(ret => {
        if (ret.status === 'success') {
          window.localStorage.setItem('authToken', ret.auth_token)
          getProfile(dispatch)
        } else {
          dispatch(AuthError(ret.message))
        }
      })
      .catch(error => {
        throw error
      })
  }
}

export function loadProfile() {
  if (window.localStorage.getItem('authToken')) {
    return function(dispatch) {
      getProfile(dispatch)
    }
  }
  return { type: 'LOGOUT' }
}

export function logout() {
  return { type: 'LOGOUT' }
}

export function handleUserFormSubmit(event, formType) {
  event.preventDefault()
  return (dispatch, getState) => {
    const state = getState()
    let { formData } = state.formData
    formData.formData = state.formData.formData
    if (formType === 'Login') {
      dispatch(login(formData.formData))
    } else { // formType === 'Register'
      dispatch(register(formData.formData))
    }
  }
}

export const handleFormChange = event => dispatch => {
  switch (event.target.name) {
    case 'email':
      return dispatch(updateFormDataEmail(event.target.value))
    case 'username':
      return dispatch(updateFormDataUsername(event.target.value))
    default: // case 'password':
      return dispatch(updateFormDataPassword(event.target.value))
  }
}
