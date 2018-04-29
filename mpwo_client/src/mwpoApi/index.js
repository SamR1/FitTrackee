import { apiUrl } from '../utils'

export default class MpwoApi {

  static getData(target) {
    const request = new Request(`${apiUrl}${target}`, {
      method: 'GET',
      headers: new Headers({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${window.localStorage.getItem('authToken')}`,
      }),
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }
}
