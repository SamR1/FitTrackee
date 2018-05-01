import mpwoApi from '../mwpoApi/activities'
import { history } from '../index'
import { setError } from './index'


export function addActivity(form) {
  return function(dispatch) {
    return mpwoApi
    .addActivity(form)
    .then(ret => {
      if (ret.status === 'created') {
        history.push('/')
      } else {
        dispatch(setError(`activities: ${ret.message}`))
      }
    })
    .catch(error => dispatch(setError(`activities: ${error}`)))
  }
}
