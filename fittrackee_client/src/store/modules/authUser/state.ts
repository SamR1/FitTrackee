import { IAuthUserState } from '@/store/modules/authUser/types'
import { IUserProfile } from '@/types/user'

export const authUserState: IAuthUserState = {
  authToken: null,
  authUserProfile: <IUserProfile>{},
  loading: false,
}
