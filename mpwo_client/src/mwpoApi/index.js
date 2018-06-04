import { apiUrl, createRequest } from '../utils'

export default class MpwoApi {

  static getData(target,
                 data = {}) {
    let url = `${apiUrl}${target}`
    if (data.id) {
      url = `${url}/${data.id}`
    } else if (data.page) {
      url = `${url}?page=${data.page}`
    }
    if (data.start || data.end) {
      url = `${url}${
      data.page ? '' : '?'
        }${
      data.start && `&from=${data.start}`
        }${
      data.end && `&to=${data.end}`
        }`
    }
    if (data.order) {
      url = `${url}${
        (data.page || data.start || data.end) ? '' : '?'
      }${
        `&order=${data.order}`
      }`
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
