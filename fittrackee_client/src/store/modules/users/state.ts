import { IUsersState } from '@/store/modules/users/types'
import { IPagination } from '@/types/api'

export const usersState: IUsersState = {
  users: [],
  loading: false,
  pagination: <IPagination>{},
}
