import { apiUrl, createRequest } from '../utils'

export default class FitTrackeeApi {

  static getData(target,
                 data = {}) {
    let url = `${apiUrl}${target}`
    if (data.id) {
      url = `${url}/${data.id}`
    } else if (Object.keys(data).length > 0) {
      url += '?'
      Object.keys(data).map(key => url += `&${key}=${data[key]}`)
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

  static addDataWithFile(target, data) {
    const params = {
      url: `${apiUrl}${target}`,
      method: 'POST',
      body: data,
    }
    return createRequest(params)
  }

  static postData(target, data) {
    const params = {
      url: `${apiUrl}${target}${data.id ? `/${data.id}` : '' }`,
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
