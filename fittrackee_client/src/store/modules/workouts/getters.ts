import { GetterTree } from 'vuex'

import { WORKOUTS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import {
  IWorkoutsGetters,
  IWorkoutsState,
} from '@/store/modules/workouts/types'

export const getters: GetterTree<IWorkoutsState, IRootState> &
  IWorkoutsGetters = {
  [WORKOUTS_STORE.GETTERS.CALENDAR_WORKOUTS]: (state: IWorkoutsState) => {
    return state.calendar_workouts
  },
  [WORKOUTS_STORE.GETTERS.USER_WORKOUTS]: (state: IWorkoutsState) => {
    return state.user_workouts
  },
}
