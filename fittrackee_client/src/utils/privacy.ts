import type { TPrivacyLevels } from '@/types/user'

export const getPrivacyLevels = (
  federationEnabled: boolean
): TPrivacyLevels[] => {
  return federationEnabled
    ? ['private', 'followers_only', 'followers_and_remote_only', 'public']
    : ['private', 'followers_only', 'public']
}

export const getPrivacyLevelForLabel = (
  privacyLevel: TPrivacyLevels | null | undefined,
  federationEnabled: boolean
): string => {
  if (!privacyLevel) {
    return ''
  }
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
  // regardless federation activation, map can not be visible
  // to remote followers
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

export const getCommentVisibilityLevels = (
  workoutVisibility: TPrivacyLevels,
  federationEnabled: boolean
): TPrivacyLevels[] => {
  switch (workoutVisibility) {
    case 'public':
      return federationEnabled
        ? ['private', 'followers_only', 'followers_and_remote_only', 'public']
        : ['private', 'followers_only', 'public']
    // Note: only if federation is still enabled
    case 'followers_and_remote_only':
      return federationEnabled
        ? ['private', 'followers_only', 'followers_and_remote_only']
        : ['private', 'followers_only']
    case 'followers_only':
      return ['private', 'followers_only']
    // Note: it's not possible to add comment to a private workout
    case 'private':
      return ['private']
  }
}
