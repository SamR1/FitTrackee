import { TPrivacyLevels } from '@/types/user'

export const getPrivacyLevels = (): TPrivacyLevels[] => {
  return ['private', 'followers_only', 'public']
}
export const getUpdatedMapVisibility = (
  mapVisibility: TPrivacyLevels,
  workoutVisibility: TPrivacyLevels
): TPrivacyLevels => {
  // when workout visibility is stricter, it returns workout visibility value
  // for map visibility
  if (
    workoutVisibility === 'private' ||
    (workoutVisibility === 'followers_only' && mapVisibility == 'public')
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
    case 'followers_only':
      return ['private', 'followers_only']
    case 'private':
      return ['private']
  }
}

export const getCommentVisibilityLevels = (
  workoutVisibility: TPrivacyLevels
): TPrivacyLevels[] => {
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
