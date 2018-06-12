import FitTrackeeApi from '../fitTrackeeApi/user'
import { history } from '../index'
import { generateIds } from '../utils'
import { getData } from './index'


const AuthError = message => ({ type: 'AUTH_ERROR', message })

const AuthErrors = messages => ({ type: 'AUTH_ERRORS', messages })

const PictureError = message => ({ type: 'PICTURE_ERROR', message })

const ProfileSuccess = profil => ({ type: 'PROFILE_SUCCESS', profil })

const ProfileError = message => ({ type: 'PROFILE_ERROR', message })

const ProfileUpdateError = message => ({
  type: 'PROFILE_UPDATE_ERROR', message
})

export const getProfile = () => dispatch => FitTrackeeApi
  .getProfile()
  .then(ret => {
    if (ret.status === 'success') {
      dispatch(getData('sports'))
      ret.data.isAuthenticated = true
      return dispatch(ProfileSuccess(ret.data))
    }
    return dispatch(ProfileError(ret.message))
  })
  .catch(error => {
    throw error
  })


export const register = formData => dispatch => FitTrackeeApi
  .register(formData)
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


export const login = formData => dispatch => FitTrackeeApi
  .login(formData)
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

export const loadProfile = () => dispatch => {
  if (window.localStorage.getItem('authToken')) {
    return dispatch(getProfile())
  }
  return { type: 'LOGOUT' }
}

export const logout = () => ({ type: 'LOGOUT' })

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
  if (formType === 'Login') {
    return dispatch(login(formData))
  }
  // formType === 'Register'
  const ret = RegisterFormControl(formData)
  if (ret.length === 0) {
    return dispatch(register(formData))
  }
  return dispatch(AuthErrors(generateIds(ret)))
}

export const handleProfileFormSubmit = formData => dispatch => {
  if (!formData.password === formData.password_conf) {
    return dispatch(ProfileUpdateError(
      'Password and password confirmation don\'t match.'
    ))
  }
  return FitTrackeeApi
    .updateProfile(formData)
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
  return FitTrackeeApi
    .updatePicture(form)
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
    if (ret.status === 'success') {
      return dispatch(getProfile())
    }
    dispatch(PictureError(ret.message))
  })
  .catch(error => {
    throw error
  })
