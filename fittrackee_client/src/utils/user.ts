import { IAuthUserProfile, IUserProfile } from '@/types/user'

export const isAuthUser = (
  user: IUserProfile,
  authUser?: IAuthUserProfile
): boolean => !user.is_remote && user.username === authUser?.username
