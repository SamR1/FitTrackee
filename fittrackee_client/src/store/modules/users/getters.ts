import { GetterTree } from 'vuex'

import { USERS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IUsersGetters, IUsersState } from '@/store/modules/users/types'

export const getters: GetterTree<IUsersState, IRootState> & IUsersGetters = {
  [USERS_STORE.GETTERS.USERS]: (state: IUsersState) => {
    return state.users
  },
  [USERS_STORE.GETTERS.USERS_LOADING]: (state: IUsersState) => {
    return state.loading
  },
  [USERS_STORE.GETTERS.USERS_PAGINATION]: (state: IUsersState) => {
    return state.pagination
  },
}
