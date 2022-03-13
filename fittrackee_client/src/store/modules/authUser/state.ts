import { IAuthUserState } from '@/store/modules/authUser/types'
import { IAuthUserProfile } from '@/types/user'

export const authUserState: IAuthUserState = {
  authToken: null,
  authUserProfile: <IAuthUserProfile>{},
  isSuccess: false,
  loading: false,
}
