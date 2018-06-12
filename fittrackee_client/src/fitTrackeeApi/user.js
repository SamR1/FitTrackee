import { apiUrl, createRequest } from '../utils'

export default class FitTrackeeApi {

  static login(data) {
    const params = {
      url: `${apiUrl}auth/login`,
      method: 'POST',
      noAuthorization: true,
      body: data,
      type: 'application/json',
    }
    return createRequest(params)
  }

  static register(data) {
    const params = {
      url: `${apiUrl}auth/register`,
      method: 'POST',
      noAuthorization: true,
      body: data,
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

  static updateProfile(data) {
    const params = {
      url: `${apiUrl}auth/profile/edit`,
      method: 'POST',
      body: data,
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
