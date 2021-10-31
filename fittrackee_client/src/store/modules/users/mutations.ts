import { MutationTree } from 'vuex'

import { USERS_STORE } from '@/store/constants'
import { IUsersState, TUsersMutations } from '@/store/modules/users/types'
import { IPagination } from '@/types/api'
import { IUserProfile } from '@/types/user'

export const mutations: MutationTree<IUsersState> & TUsersMutations = {
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
