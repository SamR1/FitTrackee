import type { GetterTree } from 'vuex'

import { USERS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { IUsersGetters, IUsersState } from '@/store/modules/users/types'

export const getters: GetterTree<IUsersState, IRootState> & IUsersGetters = {
  [USERS_STORE.GETTERS.USER]: (state: IUsersState) => {
    return state.user
  },
  [USERS_STORE.GETTERS.USERS]: (state: IUsersState) => {
    return state.users
  },
  [USERS_STORE.GETTERS.USERS_IS_SUCCESS]: (state: IUsersState) => {
    return state.isSuccess
  },
  [USERS_STORE.GETTERS.USERS_LOADING]: (state: IUsersState) => {
    return state.loading
  },
  [USERS_STORE.GETTERS.USERS_PAGINATION]: (state: IUsersState) => {
    return state.pagination
  },
}
