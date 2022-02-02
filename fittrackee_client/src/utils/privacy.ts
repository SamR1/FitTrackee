import { TPrivacyLevels } from '@/types/user'

export const privacyLevels: TPrivacyLevels[] = [
  'private',
  'followers_only',
  'public',
]

export const getUpdatedMapVisibility = (
  mapVisibility: TPrivacyLevels,
  workoutVisibility: TPrivacyLevels
): TPrivacyLevels => {
  // when workout visibility is stricter, it returns workout visibility value
  // for map visibility
  if (
    workoutVisibility === 'private' ||
    (workoutVisibility === 'followers_only' && mapVisibility === 'public')
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
      return privacyLevels
    case 'followers_only':
      return ['private', 'followers_only']
    case 'private':
      return ['private']
  }
}
