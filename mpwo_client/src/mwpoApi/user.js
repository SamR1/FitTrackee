import { apiUrl, createRequest } from '../utils'

export default class MpwoApiUser {

  static login(email, password) {
    const params = {
      url: `${apiUrl}auth/login`,
      method: 'POST',
      noAuthorization: true,
      body: {
        email: email,
        password: password,
      },
      type: 'application/json',
    }
    return createRequest(params)
  }

  static register(username, email, password, passwordConf) {
    const params = {
      url: `${apiUrl}auth/register`,
      method: 'POST',
      noAuthorization: true,
      body: {
        username: username,
        email: email,
        password: password,
        password_conf: passwordConf,
      },
      type: 'application/json',
    }
    return createRequest(params)
  }

  static getProfile() {
    const params = {
      url: `${apiUrl}auth/profile`,
      method: 'GET',
      type: 'application/json',
    }
    return createRequest(params)
  }

  static updateProfile(form) {
    const params = {
      url: `${apiUrl}auth/profile/edit`,
      method: 'POST',
      body: {
        first_name: form.firstName,
        last_name: form.lastName,
        bio: form.bio,
        location: form.location,
        birth_date: form.birthDate,
        password: form.password,
        password_conf: form.passwordConf,
      },
      type: 'application/json',
    }
    return createRequest(params)
  }

  static updatePicture(form) {
    const params = {
      url: `${apiUrl}auth/picture`,
      method: 'POST',
      body: form,
    }
    return createRequest(params)
  }

  static deletePicture() {
    const params = {
      url: `${apiUrl}auth/picture`,
      method: 'DELETE',
    }
    return createRequest(params)
  }
}
