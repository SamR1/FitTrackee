import { MutationTree } from 'vuex'

import { WORKOUTS_STORE } from '@/store/constants'
import {
  IWorkoutsState,
  TWorkoutsMutations,
} from '@/store/modules/workouts/types'
import { IWorkout } from '@/types/workouts'

export const mutations: MutationTree<IWorkoutsState> & TWorkoutsMutations = {
  [WORKOUTS_STORE.MUTATIONS.SET_CALENDAR_WORKOUTS](
    state: IWorkoutsState,
    workouts: IWorkout[]
  ) {
    state.calendar_workouts = workouts
  },
  [WORKOUTS_STORE.MUTATIONS.SET_USER_WORKOUTS](
    state: IWorkoutsState,
    workouts: IWorkout[]
  ) {
    state.user_workouts = workouts
  },
  [WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUTS](state: IWorkoutsState) {
    state.calendar_workouts = []
    state.user_workouts = []
  },
}
