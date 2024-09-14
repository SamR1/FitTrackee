import type { GetterTree } from 'vuex'

import { WORKOUTS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type {
  IWorkoutsGetters,
  IWorkoutsState,
} from '@/store/modules/workouts/types'

export const getters: GetterTree<IWorkoutsState, IRootState> &
  IWorkoutsGetters = {
  [WORKOUTS_STORE.GETTERS.CALENDAR_WORKOUTS]: (state: IWorkoutsState) => {
    return state.calendar_workouts
  },
  [WORKOUTS_STORE.GETTERS.TIMELINE_WORKOUTS]: (state: IWorkoutsState) => {
    return state.timeline_workouts
  },
  [WORKOUTS_STORE.GETTERS.USER_WORKOUTS]: (state: IWorkoutsState) => {
    return state.user_workouts
  },
  [WORKOUTS_STORE.GETTERS.WORKOUT_CONTENT_EDITION]: (state: IWorkoutsState) => {
    return state.workoutContent
  },
  [WORKOUTS_STORE.GETTERS.WORKOUT_DATA]: (state: IWorkoutsState) => {
    return state.workoutData
  },
  [WORKOUTS_STORE.GETTERS.WORKOUTS_PAGINATION]: (state: IWorkoutsState) => {
    return state.pagination
  },
}
