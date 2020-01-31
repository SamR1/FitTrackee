const pathInterceptor = toPath => {
  if (
    !window.localStorage.authToken &&
    !['/login', '/register'].includes(toPath.pathname)
  ) {
    toPath.pathname = '/login'
  }
  if (
    window.localStorage.authToken &&
    ['/login', '/register'].includes(toPath.pathname)
  ) {
    toPath.pathname = '/'
  }
  return toPath
}

export const historyEnhancer = originalHistory => {
  originalHistory.location = pathInterceptor(originalHistory.location)
  return {
    ...originalHistory,
    push: (path, ...args) =>
      originalHistory.push(pathInterceptor(path), ...args),
    replace: (path, ...args) =>
      originalHistory.replace(pathInterceptor(path), ...args),
  }
}
