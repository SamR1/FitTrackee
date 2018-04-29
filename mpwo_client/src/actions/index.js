import mpwoApi from '../mwpoApi/index'


export const setData = (target, data) => ({
  type: 'SET_DATA',
  data,
  target,
})

export const setError = (target, error) => ({
  type: 'SET_ERROR',
  error,
  target,
})

export function getData(target) {
  return function(dispatch) {
    return mpwoApi
      .getData(target)
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(setData(target, ret.data))
      } else {
        dispatch(setError(target, ret.message))
      }
    })
    .catch(error => {
      throw error
    })
  }
}
