import { apiUrl, createRequest } from '../utils'

export default class FitTrackeeApi {

  static addActivity(formData) {
    const params = {
      url: `${apiUrl}activities`,
      method: 'POST',
      body: formData,
    }
    return createRequest(params)
  }

  static addActivityWithoutGpx(data) {
    const params = {
      url: `${apiUrl}activities/no_gpx`,
      method: 'POST',
      body: data,
      type: 'application/json',
    }
    return createRequest(params)
  }

  static getActivityGpx(activityId) {
    const params = {
      url: `${apiUrl}activities/${activityId}/gpx`,
      method: 'GET',
    }
    return createRequest(params)
  }

  static getActivityChartData(activityId) {
    const params = {
      url: `${apiUrl}activities/${activityId}/chart_data`,
      method: 'GET',
    }
    return createRequest(params)
  }

}
