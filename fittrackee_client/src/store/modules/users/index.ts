import type { Module } from 'vuex'

import type { IRootState } from '@/store/modules/root/types'
import { actions } from '@/store/modules/users/actions'
import { getters } from '@/store/modules/users/getters'
import { mutations } from '@/store/modules/users/mutations'
import { usersState } from '@/store/modules/users/state'
import type { IUsersState } from '@/store/modules/users/types'

const users: Module<IUsersState, IRootState> = {
  state: usersState,
  actions,
  getters,
  mutations,
}

export default users
