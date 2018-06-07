import FitTrackeeApi from '../fitTrackeeApi/stats'
import { setData, setError } from './index'

export const getStats = (userId, type, data) => dispatch => FitTrackeeApi
    .getStats(userId, type, data)
    .then(ret => {
      if (ret.status === 'success') {
         dispatch(setData('statistics', ret.data))
      } else {
        dispatch(setError(`statistics: ${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`statistics: ${error}`)))
