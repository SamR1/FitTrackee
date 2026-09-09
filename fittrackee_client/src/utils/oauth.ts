export const oauth2_scopes = [
  'equipments:read',
  'equipments:write',
  'follow:read',
  'follow:write',
  'geocode:read',
  'media:write',
  'notifications:read',
  'notifications:write',
  'profile:read',
  'profile:write',
  'reports:read',
  'reports:write',
  'users:read',
  'users:write',
  'workouts:read',
  'workouts:write',
]

export const admin_oauth2_scopes = ['application:write']

export const isUriSchemeValid = (redirectUri: string): boolean => {
  try {
    const url = new URL(redirectUri)
    return ['http:', 'https:', 'myapp:', 'app:', 'indoorbike:'].includes(
      url.protocol
    )
  } catch {
    return false
  }
}
