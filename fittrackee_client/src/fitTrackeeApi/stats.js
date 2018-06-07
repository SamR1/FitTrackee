import { apiUrl, createRequest } from '../utils'

export default class FitTrackeeApi {

  static getStats(userID, type, data = {}) {
    let url = `${apiUrl}stats/${userID}/${type}`
    if (Object.keys(data).length > 0) {
      url += '?'
      Object.keys(data).map(key => url += `&${key}=${data[key]}`)
    }
    const params = {
      url: url,
      method: 'GET',
    }
    return createRequest(params)
  }

}
