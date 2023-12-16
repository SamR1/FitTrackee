import type { Module } from 'vuex'

import type { IRootState } from '@/store/modules/root/types'
import { actions } from '@/store/modules/workouts/actions'
import { getters } from '@/store/modules/workouts/getters'
import { mutations } from '@/store/modules/workouts/mutations'
import { workoutsState } from '@/store/modules/workouts/state'
import type { IWorkoutsState } from '@/store/modules/workouts/types'

const workouts: Module<IWorkoutsState, IRootState> = {
  state: workoutsState,
  actions,
  getters,
  mutations,
}

export default workouts
