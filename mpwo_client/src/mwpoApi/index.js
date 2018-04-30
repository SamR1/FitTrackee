import { apiUrl } from '../utils'

export default class MpwoApi {

  static getData(target, id = null) {
    const request = new Request(`${apiUrl}${target}${id ? `/${id}` : ''}`, {
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

  static addData(target, data) {
    const request = new Request(`${apiUrl}${target}`, {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${window.localStorage.getItem('authToken')}`,
      }),
      body: JSON.stringify(data)
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }

  static updateData(target, data) {
    const request = new Request(`${apiUrl}${target}/${data.id}`, {
      method: 'PATCH',
      headers: new Headers({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${window.localStorage.getItem('authToken')}`,
      }),
      body: JSON.stringify(data)
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }

  static deleteData(target, id) {
    const request = new Request(`${apiUrl}${target}/${id}`, {
      method: 'DELETE',
      headers: new Headers({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${window.localStorage.getItem('authToken')}`,
      }),
    })
    return fetch(request)
      .then(response => response)
      .catch(error => error)
  }
}
