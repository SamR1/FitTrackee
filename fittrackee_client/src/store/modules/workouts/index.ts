import { Module } from 'vuex'

import { IRootState } from '@/store/modules/root/types'
import { actions } from '@/store/modules/workouts/actions'
import { getters } from '@/store/modules/workouts/getters'
import { mutations } from '@/store/modules/workouts/mutations'
import { workoutsState } from '@/store/modules/workouts/state'
import { IWorkoutsState } from '@/store/modules/workouts/types'

const workouts: Module<IWorkoutsState, IRootState> = {
  state: workoutsState,
  actions,
  getters,
  mutations,
}
