import mpwoApi from '../mwpoApi/index'
import { history } from '../index'


export const setData = (target, data) => ({
  type: 'SET_DATA',
  data,
  target,
})

export const setError = message => ({
  type: 'SET_ERROR',
  message,
})

export function getData(target, id = null) {
  return function(dispatch) {
    if (id !== null && isNaN(id)) {
      return dispatch(setError(target, `${target}: Incorrect id`))
    }
    return mpwoApi
    .getData(target, id)
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(setData(target, ret.data))
      } else {
        dispatch(setError(`${target}: ${ret.status}`))
      }
    })
    .catch(error => dispatch(setError(`${target}: ${error}`)))
  }
}

export function addData(target, data) {
  return function(dispatch) {
    if (isNaN(data.id)) {
      return dispatch(setError(target, `${target}: Incorrect id`))
    }
    return mpwoApi
    .addData(target, data)
    .then(ret => {
      if (ret.status === 'created') {
        dispatch(setData(target, ret.data))
      } else {
        dispatch(setError(`${target}: ${ret.status}`))
      }
    })
    .catch(error => dispatch(setError(`${target}: ${error}`)))
  }
}

export function updateData(target, data) {
  return function(dispatch) {
    if (isNaN(data.id)) {
      return dispatch(setError(target, `${target}: Incorrect id`))
    }
    return mpwoApi
    .updateData(target, data)
    .then(ret => {
      if (ret.status === 'success') {
        dispatch(setData(target, ret.data))
      } else {
        dispatch(setError(`${target}: ${ret.status}`))
      }
    })
    .catch(error => dispatch(setError(`${target}: ${error}`)))
  }
}

export function deleteData(target, id) {
  return function(dispatch) {
    if (isNaN(id)) {
      return dispatch(setError(target, `${target}: Incorrect id`))
    }
    return mpwoApi
    .deleteData(target, id)
    .then(ret => {
      if (ret.status === 204) {
        history.push(`/admin/${target}`)
      } else {
        dispatch(setError(`${target}: ${ret.status}`))
      }
    })
    .catch(error => dispatch(setError(`${target}: ${error}`)))
  }
}
