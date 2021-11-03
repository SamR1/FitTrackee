import { Module } from 'vuex'

import { actions } from '@/store/modules/authUser/actions'
import { getters } from '@/store/modules/authUser/getters'
import { mutations } from '@/store/modules/authUser/mutations'
import { authUserState } from '@/store/modules/authUser/state.ts'
import { IAuthUserState } from '@/store/modules/authUser/types'
import { IRootState } from '@/store/modules/root/types'

const authUser: Module<IAuthUserState, IRootState> = {
  state: authUserState,
  actions,
  getters,
  mutations,
}

export default authUser
