import { MutationTree } from 'vuex'

import { USERS_STORE } from '@/store/constants'
import { IUsersState, TUsersMutations } from '@/store/modules/users/types'
import { IPagination } from '@/types/api'
import { IUserProfile } from '@/types/user'
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
}
