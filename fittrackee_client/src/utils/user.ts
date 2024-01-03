import type { IAuthUserProfile, IUserProfile } from '@/types/user'

export const isAuthUser = (
  user: IUserProfile,
  authUser?: IAuthUserProfile
): boolean => !user.is_remote && user.username === authUser?.username

export const getUserName = (user: IUserProfile): string =>
  user.is_remote && user.fullname ? user.fullname : user.username
