import keyIndex from 'react-key-index'

import mpwoApi from '../mpwoApi'
import { history } from '../index'

function AuthError(message) {
  return { type: 'AUTH_ERROR', message }
}

function AuthErrors(messages) {
  return { type: 'AUTH_ERRORS', messages }
}

function PictureError(message) {
  return { type: 'PICTURE_ERROR', message }
}

function ProfileSuccess(message) {
  return { type: 'PROFILE_SUCCESS', message }
}

function ProfileError(message) {
  return { type: 'PROFILE_ERROR', message }
}

function PwdError(message) {
  return { type: 'PWD_ERROR', message }
}

function initProfileFormData(user) {
  return { type: 'INIT_PROFILE_FORM', user }
}

export const handleFormChange = (target, value) => ({
  type: 'UPDATE_USER_FORMDATA',
  target,
  value,
})

export const updateProfileFormData = (target, value) => ({
  type: 'UPDATE_PROFILE_FORMDATA',
  target,
  value,
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
      .register(
        formData.username,
        formData.email,
        formData.password,
        formData.passwordConf)
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

function RegisterFormControl (formData) {
  const errMsg = []
  if (formData.username.length < 3 || formData.username.length > 12) {
    errMsg.push('Username: 3 to 12 characters required.')
  }
  if (formData.password !== formData.passwordConf) {
    errMsg.push('Password and password confirmation don\'t match.')
  }
  if (formData.password.length < 8) {
    errMsg.push('Password: 8 characters required.')
  }
  return errMsg
}

export function handleUserFormSubmit(event, formType) {
  event.preventDefault()
  return (dispatch, getState) => {
    const state = getState()
    const { formData } = state.formData
    formData.formData = state.formData.formData
    if (formType === 'Login') {
      dispatch(login(formData.formData))
    } else { // formType === 'Register'
      const ret = RegisterFormControl(formData.formData)
      if (ret.length === 0) {
        dispatch(register(formData.formData))
      } else {
        dispatch(AuthErrors(keyIndex(ret, 1)))
      }
    }
  }
}

export function initProfileForm () {
  return (dispatch, getState) => {
    const state = getState()
    dispatch(initProfileFormData(state.user))
  }
}

export function handleProfileFormSubmit(event) {
  event.preventDefault()
  return (dispatch, getState) => {
    const state = getState()
    if (!state.formProfile.formProfile.password ===
        state.formProfile.formProfile.passwordConf) {
      dispatch(PwdError('Password and password confirmation don\'t match.'))
    } else {
      return mpwoApi
      .updateProfile(state.formProfile.formProfile)
      .then(ret => {
        if (ret.status === 'success') {
          getProfile(dispatch)
          history.push('/profile')
        } else {
          dispatch(AuthError(ret.message))
        }
      })
      .catch(error => {
        throw error
      })
    }

  }
}

export function uploadPicture (event) {
  event.preventDefault()
  const form = new FormData()
  form.append('file', event.target.picture.files[0])
  event.target.reset()
  return function(dispatch) {
    return mpwoApi
      .updatePicture(form)
      .then(ret => {
        if (ret.status === 'success') {
          getProfile(dispatch)
        } else {
          dispatch(PictureError(ret.message))
        }
      })
      .catch(error => {
        throw error
      })
  }
}

export function deletePicture() {
  return function(dispatch) {
  return mpwoApi
    .deletePicture()
    .then(ret => {
      if (ret.status === 'success') {
        getProfile(dispatch)
      } else {
        dispatch(PictureError(ret.message))
      }
    })
    .catch(error => {
      throw error
    })
  }
}
