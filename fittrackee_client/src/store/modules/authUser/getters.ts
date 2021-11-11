import { GetterTree } from 'vuex'

import { AUTH_USER_STORE } from '@/store/constants'
import {
  IAuthUserGetters,
  IAuthUserState,
} from '@/store/modules/authUser/types'
import { IRootState } from '@/store/modules/root/types'

export const getters: GetterTree<IAuthUserState, IRootState> &
  IAuthUserGetters = {
  [AUTH_USER_STORE.GETTERS.AUTH_TOKEN]: (state: IAuthUserState) => {
    return state.authToken
  },
  [AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]: (state: IAuthUserState) => {
    return state.authUserProfile
  },
  [AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED]: (state: IAuthUserState) => {
    return state.authToken !== null
  },
  [AUTH_USER_STORE.GETTERS.IS_ADMIN]: (state: IAuthUserState) => {
    return state.authUserProfile && state.authUserProfile.admin
  },
  [AUTH_USER_STORE.GETTERS.USER_LOADING]: (state: IAuthUserState) => {
    return state.loading
  },
}
