import { createApiRequest } from '../utils'

export default class FitTrackeeApi {
  static getData(target, data = {}) {
    let url = target
    if (data.id || (target === 'users' && data.username)) {
      url = `${url}/${data.username ? data.username : data.id}`
    } else if (Object.keys(data).length > 0) {
      url += '?'
      Object.keys(data).map(key => (url += `&${key}=${data[key]}`))
    }
    const params = {
      url: url,
      method: 'GET',
      type: 'application/json',
    }
    return createApiRequest(params)
  }

  static addData(target, data) {
    const params = {
      url: target,
      method: 'POST',
      body: data,
      type: 'application/json',
    }
    return createApiRequest(params)
  }

  static addDataWithFile(target, data) {
    const params = {
      url: target,
      method: 'POST',
      body: data,
    }
    return createApiRequest(params)
  }

  static postData(target, data) {
    const params = {
      url: `${target}${data.id ? `/${data.id}` : ''}`,
      method: 'POST',
      body: data,
      type: 'application/json',
    }
    return createApiRequest(params)
  }

  static updateData(target, data) {
    const params = {
      url: `${target}${
        data.id ? `/${data.id}` : data.username ? `/${data.username}` : ''
      }`,
      method: 'PATCH',
      body: data,
      type: 'application/json',
    }
    return createApiRequest(params)
  }

  static deleteData(target, id) {
    const params = {
      url: `${target}/${id}`,
      method: 'DELETE',
      type: 'application/json',
    }
    return createApiRequest(params)
  }
}
