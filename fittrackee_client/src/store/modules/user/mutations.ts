import { MutationTree } from 'vuex'

import { USER_STORE } from '@/store/constants'
import { IAuthUserProfile, IUserState } from '@/store/modules/user/interfaces'
import { TUserMutations } from '@/store/modules/user/types'

export const mutations: MutationTree<IUserState> & TUserMutations = {
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
