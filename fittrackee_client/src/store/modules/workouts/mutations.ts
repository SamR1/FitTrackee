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
}
