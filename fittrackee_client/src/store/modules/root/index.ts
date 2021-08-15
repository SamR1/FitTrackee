import { Module, ModuleTree } from 'vuex'

import { actions } from '@/store/modules/root/actions'
import { getters } from '@/store/modules/root/getters'
import { IRootState } from '@/store/modules/root/interfaces'
import { mutations } from '@/store/modules/root/mutations'
import { state } from '@/store/modules/root/state.ts'
import userModule from '@/store/modules/user'

const modules: ModuleTree<IRootState> = {
  userModule,
}

const root: Module<IRootState, IRootState> = {
  state,
  actions,
  getters,
  mutations,
  modules,
}

export default root
