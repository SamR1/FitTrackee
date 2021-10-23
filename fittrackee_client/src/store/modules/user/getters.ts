import { GetterTree } from 'vuex'

import { USER_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IUserGetters, IUserState } from '@/store/modules/user/types'

export const getters: GetterTree<IUserState, IRootState> & IUserGetters = {
  [USER_STORE.GETTERS.AUTH_TOKEN]: (state: IUserState) => {
    return state.authToken
  },
  [USER_STORE.GETTERS.AUTH_USER_PROFILE]: (state: IUserState) => {
    return state.authUserProfile
  },
  [USER_STORE.GETTERS.IS_AUTHENTICATED]: (state: IUserState) => {
    return state.authToken !== null
  },
  [USER_STORE.GETTERS.IS_ADMIN]: (state: IUserState) => {
    return state.authUserProfile && state.authUserProfile.admin
  },
  [USER_STORE.GETTERS.USER_LOADING]: (state: IUserState) => {
    return state.loading
  },
}
