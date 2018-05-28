import { apiUrl, createRequest } from '../utils'

export default class MpwoApi {

  static getData(target, id = null, page = null) {
    let url = `${apiUrl}${target}`
    if (id) {
      url = `${url}/${id}`
    } else if (page) {
      url = `${url}?page=${page}`
    }
    const params = {
      url: url,
      method: 'GET',
      type: 'application/json',
    }
    return createRequest(params)
  }

  static addData(target, data) {
    const params = {
      url: `${apiUrl}${target}`,
      method: 'POST',
      body: data,
      type: 'application/json',
    }
    return createRequest(params)
  }

  static updateData(target, data) {
    const params = {
      url: `${apiUrl}${target}/${data.id}`,
      method: 'PATCH',
      body: data,
      type: 'application/json',
    }
    return createRequest(params)
  }

  static deleteData(target, id) {
    const params = {
      url: `${apiUrl}${target}/${id}`,
      method: 'DELETE',
      type: 'application/json',
    }
    return createRequest(params)
  }
}
