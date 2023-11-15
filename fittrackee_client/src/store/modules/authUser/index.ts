import type { Module } from 'vuex'

import { actions } from '@/store/modules/authUser/actions'
import { getters } from '@/store/modules/authUser/getters'
import { mutations } from '@/store/modules/authUser/mutations'
import { authUserState } from '@/store/modules/authUser/state'
import type { IAuthUserState } from '@/store/modules/authUser/types'
import type { IRootState } from '@/store/modules/root/types'

const authUser: Module<IAuthUserState, IRootState> = {
  state: authUserState,
  actions,
  getters,
  mutations,
}

export default authUser
