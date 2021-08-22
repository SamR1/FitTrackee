import { MutationTree } from 'vuex'

import { USER_STORE } from '@/store/constants'
import { IUserState, TUserMutations } from '@/store/modules/user/types'
import { IAuthUserProfile } from '@/types/user'

export const mutations: MutationTree<IUserState> & TUserMutations = {
  [USER_STORE.MUTATIONS.CLEAR_AUTH_USER_TOKEN](state: IUserState) {
    state.authToken = null
    state.authUserProfile = <IAuthUserProfile>{}
  },
  [USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN](
    state: IUserState,
    authToken: string
  ) {
    state.authToken = authToken
  },
  [USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE](
    state: IUserState,
    authUserProfile: IAuthUserProfile
  ) {
    state.authUserProfile = authUserProfile
  },
}
