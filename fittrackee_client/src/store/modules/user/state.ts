import { IUserState } from '@/store/modules/user/types'
import { IAuthUserProfile } from '@/types/user'

export const userState: IUserState = {
  authToken: null,
  authUserProfile: <IAuthUserProfile>{},
  loading: false,
}
