import type { GetterTree } from 'vuex'

import { USERS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { IUsersGetters, IUsersState } from '@/store/modules/users/types'

export const getters: GetterTree<IUsersState, IRootState> & IUsersGetters = {
  [USERS_STORE.GETTERS.USER]: (state: IUsersState) => {
    return state.user
  },
  [USERS_STORE.GETTERS.USER_CURRENT_REPORTING]: (state: IUsersState) => {
    return state.currentReporting
  },
  [USERS_STORE.GETTERS.USER_RELATIONSHIPS]: (state: IUsersState) => {
    return state.user_relationships
  },
  [USERS_STORE.GETTERS.USER_SANCTIONS]: (state: IUsersState) => {
    return state.userSanctions.sanctions
  },
  [USERS_STORE.GETTERS.USER_SANCTIONS_LOADING]: (state: IUsersState) => {
    return state.userSanctions.loading
  },
  [USERS_STORE.GETTERS.USER_SANCTIONS_PAGINATION]: (state: IUsersState) => {
    return state.userSanctions.pagination
  },
  [USERS_STORE.GETTERS.USER_WORKOUTS]: (state: IUsersState) => {
    return state.userWorkouts.workouts
  },
  [USERS_STORE.GETTERS.USER_WORKOUTS_LOADING]: (state: IUsersState) => {
    return state.userWorkouts.loading
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
