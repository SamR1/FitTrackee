import type { TVisibilityLevels } from '@/types/user'

export const getAllVisibilityLevels = (): TVisibilityLevels[] => {
  return ['private', 'followers_only', 'public']
}

export const getUpdatedVisibility = (
  visibility: TVisibilityLevels,
  parentVisibility: TVisibilityLevels
): TVisibilityLevels => {
  if (
    parentVisibility === 'private' ||
    (parentVisibility === 'followers_only' && visibility == 'public')
  ) {
    return parentVisibility
  }
  return visibility
}

export const getVisibilityLevels = (
  inputVisibility: TVisibilityLevels
): TVisibilityLevels[] => {
  switch (inputVisibility) {
    case 'public':
      return ['private', 'followers_only', 'public']
    case 'followers_only':
      return ['private', 'followers_only']
    case 'private':
      return ['private']
  }
}

export const getCommentVisibilityLevels = (
  workoutVisibility: TVisibilityLevels
): TVisibilityLevels[] => {
  switch (workoutVisibility) {
    case 'public':
      return ['private', 'followers_only', 'public']
    case 'followers_only':
      return ['private', 'followers_only']
    // Note: it's not possible to add comment to a private workout
    case 'private':
      return ['private']
  }
}
