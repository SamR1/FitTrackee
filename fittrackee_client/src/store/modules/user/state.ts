import { IAuthUserProfile, IUserState } from '@/store/modules/user/interfaces'

export const userState: IUserState = {
  authToken: null,
  authUserProfile: <IAuthUserProfile>{},
}
