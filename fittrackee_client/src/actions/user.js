import FitTrackeeGenericApi from '../fitTrackeeApi'
import FitTrackeeApi from '../fitTrackeeApi/user'
import { history } from '../index'
import { generateIds } from '../utils'
import { getOrUpdateData } from './index'


const AuthError = message => ({ type: 'AUTH_ERROR', message })

const AuthErrors = messages => ({ type: 'AUTH_ERRORS', messages })

const PictureError = message => ({ type: 'PICTURE_ERROR', message })

const ProfileSuccess = profil => ({ type: 'PROFILE_SUCCESS', profil })

const ProfileError = message => ({ type: 'PROFILE_ERROR', message })

const ProfileUpdateError = message => ({
  type: 'PROFILE_UPDATE_ERROR', message
})

export const logout = () => ({ type: 'LOGOUT' })

export const loadProfile = () => dispatch => {
  if (window.localStorage.getItem('authToken')) {
    return dispatch(getProfile())
  }
  return { type: 'LOGOUT' }
}

export const getProfile = () => dispatch => FitTrackeeGenericApi
  .getData('auth/profile')
  .then(ret => {
    if (ret.status === 'success') {
      dispatch(getOrUpdateData('getData', 'sports'))
      ret.data.isAuthenticated = true
      return dispatch(ProfileSuccess(ret.data))
    }
    return dispatch(ProfileError(ret.message))
  })
  .catch(error => {
    throw error
  })

export const loginOrRegister = (target, formData) => dispatch => FitTrackeeApi
  .loginOrRegister(target, formData)
  .then(ret => {
    if (ret.status === 'success') {
      window.localStorage.setItem('authToken', ret.auth_token)
      return dispatch(getProfile())
    }
    return dispatch(AuthError(ret.message))
  })
  .catch(error => {
    throw error
  })

const RegisterFormControl = formData => {
  const errMsg = []
  if (formData.username.length < 3 || formData.username.length > 12) {
    errMsg.push('Username: 3 to 12 characters required.')
  }
  if (formData.password !== formData.password_conf) {
    errMsg.push('Password and password confirmation don\'t match.')
  }
  if (formData.password.length < 8) {
    errMsg.push('Password: 8 characters required.')
  }
  return errMsg
}

export const handleUserFormSubmit = (formData, formType) => dispatch => {
  if (formType === 'register') {
    const ret = RegisterFormControl(formData)
    if (ret.length > 0) {
      return dispatch(AuthErrors(generateIds(ret)))
    }
  }
  return dispatch(loginOrRegister(formType, formData))
}

export const handleProfileFormSubmit = formData => dispatch => {
  if (!formData.password === formData.password_conf) {
    return dispatch(ProfileUpdateError(
      'Password and password confirmation don\'t match.'
    ))
  }
  delete formData.id
  return FitTrackeeGenericApi
    .postData('auth/profile/edit', formData)
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(getProfile())
        return history.push('/profile')
      }
      dispatch(ProfileUpdateError(ret.message))
    })
    .catch(error => {
      throw error
    })
}

export const uploadPicture = event => dispatch => {
  event.preventDefault()
  const form = new FormData()
  form.append('file', event.target.picture.files[0])
  event.target.reset()
  return FitTrackeeGenericApi
    .addDataWithFile('auth/picture', form)
    .then(ret => {
      if (ret.status === 'success') {
        return dispatch(getProfile())
      }
      return dispatch(PictureError(ret.message))
    })
    .catch(error => {
      throw error
    })
}

export const deletePicture = () => dispatch => FitTrackeeApi
  .deletePicture()
  .then(ret => {
    if (ret.status === 204) {
      return dispatch(getProfile())
    }
    return dispatch(PictureError(ret.message))
  })
  .catch(error => {
    throw error
  })
