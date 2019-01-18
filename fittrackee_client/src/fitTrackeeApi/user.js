import { createApiRequest } from '../utils'

export default class FitTrackeeApi {

  static loginOrRegister(target, data) {
    const params = {
      url: `auth/${target}`,
      method: 'POST',
      noAuthorization: true,
      body: data,
      type: 'application/json',
    }
    return createApiRequest(params)
  }

  static deletePicture() {
    const params = {
      url: 'auth/picture',
      method: 'DELETE',
    }
    return createApiRequest(params)
  }
}
