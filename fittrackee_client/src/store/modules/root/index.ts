import type { Module, ModuleTree } from 'vuex'

import authUserModule from '@/store/modules/authUser'
import equipmentTypes from '@/store/modules/equipmentTypes'
import oAuthModule from '@/store/modules/oauth2'
import { actions } from '@/store/modules/root/actions'
import { getters } from '@/store/modules/root/getters'
import { mutations } from '@/store/modules/root/mutations'
import { state } from '@/store/modules/root/state'
import type { IRootState } from '@/store/modules/root/types'
import sportsModule from '@/store/modules/sports'
import statsModule from '@/store/modules/statistics'
import usersModule from '@/store/modules/users'
import workoutsModule from '@/store/modules/workouts'

const modules: ModuleTree<IRootState> = {
  authUserModule,
  equipmentTypes,
  oAuthModule,
  sportsModule,
  statsModule,
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
