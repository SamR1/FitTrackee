import { Module, ModuleTree } from 'vuex'
import { IRootState } from '@/store/modules/root/interfaces'
import { mutations } from '@/store/modules/root/mutations'
import { state } from '@/store/modules/root/state.ts'
import userModule from '@/store/modules/user'

const modules: ModuleTree<IRootState> = {
  userModule,
}

const root: Module<IRootState, IRootState> = {
  state,
  mutations,
  modules,
}

export default root
