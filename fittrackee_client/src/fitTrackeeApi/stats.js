import { apiUrl, createRequest } from '../utils'

export default class FitTrackeeApi {

  static getStats(userID, type, data = {}) {
    let url = `${apiUrl}stats/${userID}/${type}`
    if (Object.keys(data).length > 0) {
      url = `${url}?${
        data.start ? `&from=${data.start}` : ''
      }${
        data.end ? `&to=${data.end}` : ''
      }${
        data.time ? `&time=${data.time}` : ''
      }${
        data.sport_id ? `&sport_id=${data.sport_id}` : ''
      }`
    }
    const params = {
      url: url,
      method: 'GET',
    }
    return createRequest(params)
  }

}
