export const getCookieValue = (): string | null => {
  if (typeof document === 'undefined') {
    return null
  }

  const cookie = document.cookie
    .split(';')
    .map((value) => value.trim())
    .find((value) => value.startsWith('csrf_access_token='))

  if (!cookie) {
    return null
  }

  const [, rawValue] = cookie.split('=')
  return rawValue ? decodeURIComponent(rawValue) : null
}

export const removeCookies = (): undefined => {
  if (typeof document === 'undefined') {
    return
  }
  document.cookie = 'csrf_access_token=;expires=Thu, 01 Jan 1970 00:00:00 GMT'
}
