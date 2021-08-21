import { IUserState } from '@/store/modules/user/interfaces'
import { IAuthUserProfile } from '@/types/user'

export const userState: IUserState = {
  authToken: null,
  authUserProfile: <IAuthUserProfile>{},
}
