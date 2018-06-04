import { apiUrl, createRequest } from '../utils'

export default class MpwoApi {

  static getData(target,
                 data = {}) {
    let url = `${apiUrl}${target}`
    if (data.id) {
      url = `${url}/${data.id}`
    } else if (Object.keys(data).length > 0) {
      url = `${url}?${
        data.page ? `&page=${data.page}` : ''
        }${
        data.start ? `&from=${data.start}` : ''
          }${
        data.end ? `&to=${data.end}` : ''
          }${
        data.order ? `&order=${data.order}` : ''
        }${
        data.per_page ? `$per_page=${data.per_page}` : ''
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
