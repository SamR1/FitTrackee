import { MutationTree } from 'vuex'

import { USER_STORE } from '@/store/constants'
import { IUserState, TUserMutations } from '@/store/modules/user/types'
import { IUserProfile } from '@/types/user'

export const mutations: MutationTree<IUserState> & TUserMutations = {
  [USER_STORE.MUTATIONS.CLEAR_AUTH_USER_TOKEN](state: IUserState) {
    state.authToken = null
    state.authUserProfile = <IUserProfile>{}
  },
  [USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN](
    state: IUserState,
    authToken: string
  ) {
    state.authToken = authToken
  },
  [USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE](
    state: IUserState,
    authUserProfile: IUserProfile
  ) {
    state.authUserProfile = authUserProfile
  },
  [USER_STORE.MUTATIONS.UPDATE_USER_LOADING](
    state: IUserState,
    loading: boolean
  ) {
    state.loading = loading
  },
}
