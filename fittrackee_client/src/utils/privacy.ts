import { TPrivacyLevels } from '@/types/user'

export const getPrivacyLevels = (
  federationEnabled: boolean
): TPrivacyLevels[] => {
  return federationEnabled
    ? ['private', 'followers_only', 'followers_and_remote_only', 'public']
    : ['private', 'followers_only', 'public']
}

export const getPrivacyLevelForLabel = (
  privacyLevel: string,
  federationEnabled: boolean
): string => {
  if (privacyLevel !== 'followers_only') {
    return privacyLevel
  }
  return federationEnabled ? 'local_followers_only' : 'followers_only'
}

export const getUpdatedMapVisibility = (
  mapVisibility: TPrivacyLevels,
  workoutVisibility: TPrivacyLevels
): TPrivacyLevels => {
  // when workout visibility is stricter, it returns workout visibility value
  // for map visibility
  if (
    workoutVisibility === 'private' ||
    (workoutVisibility === 'followers_only' &&
      ['followers_and_remote_only', 'public'].includes(mapVisibility)) ||
    (workoutVisibility === 'followers_and_remote_only' &&
      mapVisibility === 'public')
  ) {
    return workoutVisibility
  }
  return mapVisibility
}

export const getMapVisibilityLevels = (
  workoutVisibility: TPrivacyLevels
): TPrivacyLevels[] => {
  switch (workoutVisibility) {
    case 'public':
      return ['private', 'followers_only', 'public']
    case 'followers_and_remote_only':
      return ['private', 'followers_only']
    case 'followers_only':
      return ['private', 'followers_only']
    case 'private':
      return ['private']
  }
}
