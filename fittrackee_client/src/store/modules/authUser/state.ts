import type { IAuthUserState } from '@/store/modules/authUser/types'
import type { IAuthUserProfile } from '@/types/user'

export const authUserState: IAuthUserState = {
  authToken: null,
  authUserProfile: <IAuthUserProfile>{},
  isSuccess: false,
  isRegistrationSuccess: false,
  loading: false,
  exportRequest: null,
  followRequests: [],
  blockedUsers: [],
}
