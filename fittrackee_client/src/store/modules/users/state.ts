import { IUsersState } from '@/store/modules/users/types'
import { IPagination } from '@/types/api'
import { IUserProfile } from '@/types/user'

export const usersState: IUsersState = {
  user: <IUserProfile>{},
  user_relationships: [],
  users: [],
  loading: false,
  isSuccess: false,
  pagination: <IPagination>{},
  currentReporting: false,
}
