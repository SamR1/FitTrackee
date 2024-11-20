import type { MutationTree } from 'vuex'

import { USERS_STORE } from '@/store/constants'
import type { IUsersState, TUsersMutations } from '@/store/modules/users/types'
import type { IPagination } from '@/types/api'
import type { IReportAction } from '@/types/reports'
import type { IUserProfile } from '@/types/user'
import { getUserName } from '@/utils/user'

export const mutations: MutationTree<IUsersState> & TUsersMutations = {
  [USERS_STORE.MUTATIONS.UPDATE_USER](state: IUsersState, user: IUserProfile) {
    state.user = user
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS](
    state: IUsersState,
    updatedUser: IUserProfile
  ) {
    state.users = state.users.map((user) => {
      if (getUserName(user) === getUserName(updatedUser)) {
        return updatedUser
      }
      return user
    })
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_IN_RELATIONSHIPS](
    state: IUsersState,
    updatedUser: IUserProfile
  ) {
    state.user_relationships = state.user_relationships.map((user) => {
      if (getUserName(user) === getUserName(updatedUser)) {
        return updatedUser
      }
      return user
    })
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_RELATIONSHIPS](
    state: IUsersState,
    relationships: IUserProfile[]
  ) {
    state.user_relationships = relationships
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS](
    state: IUsersState,
    sanctions: IReportAction[]
  ) {
    state.userSanctions.sanctions = sanctions
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS_LOADING](
    state: IUsersState,
    loading: boolean
  ) {
    state.userSanctions.loading = loading
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS_PAGINATION](
    state: IUsersState,
    pagination: IPagination
  ) {
    state.userSanctions.pagination = pagination
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
  [USERS_STORE.MUTATIONS.UPDATE_USER_CURRENT_REPORTING](
    state: IUsersState,
    currentReporting: boolean
  ) {
    state.currentReporting = currentReporting
  },
}
