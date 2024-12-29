import type { TVisibilityLevels } from '@/types/user'

export const getAllVisibilityLevels = (
  federationEnabled: boolean
): TVisibilityLevels[] => {
  return federationEnabled
    ? ['private', 'followers_only', 'followers_and_remote_only', 'public']
    : ['private', 'followers_only', 'public']
}

export const getVisibilityLevelForLabel = (
  visibilityLevel: TVisibilityLevels | null | undefined,
  federationEnabled: boolean
): string => {
  if (!visibilityLevel) {
    return ''
  }
  if (visibilityLevel !== 'followers_only') {
    return visibilityLevel
  }
  return federationEnabled ? 'local_followers_only' : 'followers_only'
}

export const getUpdatedVisibility = (
  visibility: TVisibilityLevels,
  parentVisibility: TVisibilityLevels
): TVisibilityLevels => {
  if (
    parentVisibility === 'private' ||
    (parentVisibility === 'followers_only' &&
      ['followers_and_remote_only', 'public'].includes(visibility)) ||
    (parentVisibility === 'followers_and_remote_only' &&
      visibility === 'public')
  ) {
    return parentVisibility
  }
  return visibility
}

export const getVisibilityLevels = (
  inputVisibility: TVisibilityLevels
): TVisibilityLevels[] => {
  // regardless federation activation, map can not be visible
  // to remote followers
  switch (inputVisibility) {
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
  workoutVisibility: TVisibilityLevels,
  federationEnabled: boolean
): TVisibilityLevels[] => {
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
