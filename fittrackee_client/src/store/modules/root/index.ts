import { Module, ModuleTree } from 'vuex'

import { actions } from '@/store/modules/root/actions'
import { getters } from '@/store/modules/root/getters'
import { mutations } from '@/store/modules/root/mutations'
import { state } from '@/store/modules/root/state.ts'
import { IRootState } from '@/store/modules/root/types'
import sportsModule from '@/store/modules/sports'
import statsModule from '@/store/modules/statistics'
import userModule from '@/store/modules/user'
import usersModule from '@/store/modules/users'
import workoutsModule from '@/store/modules/workouts'

const modules: ModuleTree<IRootState> = {
  sportsModule,
  statsModule,
  userModule,
  usersModule,
  workoutsModule,
}

const root: Module<IRootState, IRootState> = {
  state,
  actions,
  getters,
  mutations,
  modules,
}

export default root
