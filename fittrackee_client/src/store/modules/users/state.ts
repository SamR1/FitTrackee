import type { IUsersState } from '@/store/modules/users/types'
import type { IPagination } from '@/types/api'
import type { IUserProfile } from '@/types/user'

export const usersState: IUsersState = {
  user: <IUserProfile>{},
  userSanctions: {
    sanctions: [],
    loading: false,
    pagination: <IPagination>{},
  },
  userWorkouts: {
    workouts: [],
    loading: false,
  },
  user_relationships: [],
  users: [],
  loading: false,
  isSuccess: false,
  pagination: <IPagination>{},
  currentReporting: false,
}
