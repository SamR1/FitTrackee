import { IUserState } from '@/store/modules/user/types'
import { IUserProfile } from '@/types/user'

export const userState: IUserState = {
  authToken: null,
  authUserProfile: <IUserProfile>{},
  loading: false,
}
