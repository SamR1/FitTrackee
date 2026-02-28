import type {
  IAuthUserProfile,
  IUserLightProfile,
  IUserProfile,
} from '@/types/user'

export const isAuthUser = (
  user: IUserProfile | IUserLightProfile,
  authUser?: IAuthUserProfile
): boolean => !user.is_remote && user.username === authUser?.username

export const getUserName = (user: IUserProfile | IUserLightProfile): string =>
  user.is_remote && user.fullname ? user.fullname : user.username
