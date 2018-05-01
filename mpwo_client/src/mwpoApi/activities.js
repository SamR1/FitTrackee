import { apiUrl } from '../utils'

export default class MpwoApi {

  static addActivity(formData) {
    const request = new Request(`${apiUrl}activities`, {
      method: 'POST',
      headers: new Headers({
        Authorization: `Bearer ${window.localStorage.getItem('authToken')}`,
      }),
      body: formData,
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }

}
