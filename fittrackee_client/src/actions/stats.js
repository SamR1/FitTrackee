import FitTrackeeGenericApi from '../fitTrackeeApi'
import { setData, setError } from './index'

export const getStats = (userName, type, data) => dispatch =>
  FitTrackeeGenericApi.getData(`stats/${userName}/${type}`, data)
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(setData('statistics', ret.data))
      } else {
        dispatch(setError(`statistics|${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`statistics|${error}`)))
