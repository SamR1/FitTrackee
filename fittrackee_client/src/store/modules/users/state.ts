import { IUsersState } from '@/store/modules/users/types'
import { IPagination } from '@/types/api'
import { IUserProfile } from '@/types/user'

export const usersState: IUsersState = {
  user: <IUserProfile>{},
  users: [],
  loading: false,
  isSuccess: false,
  pagination: <IPagination>{},
}
