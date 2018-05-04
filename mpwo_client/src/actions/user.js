import mpwoApiUser from '../mwpoApi/user'
import { history } from '../index'
import { generateIds } from '../utils'


const AuthError = message => ({ type: 'AUTH_ERROR', message })

const AuthErrors = messages => ({ type: 'AUTH_ERRORS', messages })

const PictureError = message => ({ type: 'PICTURE_ERROR', message })

const ProfileSuccess = message => ({ type: 'PROFILE_SUCCESS', message })

const ProfileError = message => ({ type: 'PROFILE_ERROR', message })

const ProfileUpdateError = message => ({
  type: 'PROFILE_UPDATE_ERROR', message
})

const initProfileFormData = user => ({ type: 'INIT_PROFILE_FORM', user })

export const emptyForm = () => ({
  type: 'EMPTY_USER_FORMDATA'
})

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

export const getProfile = () => dispatch => mpwoApiUser
  .getProfile()
  .then(ret => {
    if (ret.status === 'success') {
      return dispatch(ProfileSuccess(ret))
    }
    return dispatch(ProfileError(ret.message))
  })
  .catch(error => {
    throw error
  })


export const register = formData => dispatch => mpwoApiUser
  .register(
    formData.username,
    formData.email,
    formData.password,
    formData.passwordConf)
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


export const login = formData => dispatch => mpwoApiUser
  .login(formData.email, formData.password)
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
  if (formData.password !== formData.passwordConf) {
    errMsg.push('Password and password confirmation don\'t match.')
  }
  if (formData.password.length < 8) {
    errMsg.push('Password: 8 characters required.')
  }
  return errMsg
}

export const handleUserFormSubmit = (event, formType) => (
  dispatch,
  getState
) => {
  event.preventDefault()
  const state = getState()
  const { formData } = state.formData
  formData.formData = state.formData.formData
  if (formType === 'Login') {
    return dispatch(login(formData.formData))
  }
  // formType === 'Register'
  const ret = RegisterFormControl(formData.formData)
  if (ret.length === 0) {
    return dispatch(register(formData.formData))
  }
  return dispatch(AuthErrors(generateIds(ret)))
}

export const initProfileForm = () => (dispatch, getState) => {
  const state = getState()
  return dispatch(initProfileFormData(state.user))
}

export const handleProfileFormSubmit = event => (dispatch, getState) => {
  event.preventDefault()
  const state = getState()
  if (!state.formProfile.formProfile.password ===
    state.formProfile.formProfile.passwordConf) {
    return dispatch(ProfileUpdateError(
      'Password and password confirmation don\'t match.'
    ))
  }
  return mpwoApiUser
    .updateProfile(state.formProfile.formProfile)
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
  return mpwoApiUser
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

export const deletePicture = () => dispatch => mpwoApiUser
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
