import type { MutationTree } from 'vuex'

import { USERS_STORE } from '@/store/constants'
import type { IUsersState, TUsersMutations } from '@/store/modules/users/types'
import type { IPagination } from '@/types/api'
import type { IUserProfile } from '@/types/user'

export const mutations: MutationTree<IUsersState> & TUsersMutations = {
  [USERS_STORE.MUTATIONS.UPDATE_USER](state: IUsersState, user: IUserProfile) {
    state.user = user
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS](
    state: IUsersState,
    updatedUser: IUserProfile
  ) {
    state.users = state.users.map((user) => {
      if (user.username === updatedUser.username) {
        return updatedUser
      }
      return user
    })
  },
  [USERS_STORE.MUTATIONS.UPDATE_USERS](
    state: IUsersState,
    users: IUserProfile[]
  ) {
    state.users = users
  },
  [USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING](
    state: IUsersState,
    loading: boolean
  ) {
    state.loading = loading
  },
  [USERS_STORE.MUTATIONS.UPDATE_USERS_PAGINATION](
    state: IUsersState,
    pagination: IPagination
  ) {
    state.pagination = pagination
  },
  [USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS](
    state: IUsersState,
    isSuccess: boolean
  ) {
    state.isSuccess = isSuccess
  },
}
