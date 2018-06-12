import { apiUrl, createRequest } from '../utils'

export default class FitTrackeeApi {

  static loginOrRegister(target, data) {
    const params = {
      url: `${apiUrl}auth/${target}`,
      method: 'POST',
      noAuthorization: true,
      body: data,
      type: 'application/json',
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
