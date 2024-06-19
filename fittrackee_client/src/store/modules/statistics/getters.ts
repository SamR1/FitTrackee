import type { GetterTree } from 'vuex'

import { STATS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type {
  IStatisticsGetters,
  IStatisticsState,
} from '@/store/modules/statistics/types'

export const getters: GetterTree<IStatisticsState, IRootState> &
  IStatisticsGetters = {
  [STATS_STORE.GETTERS.USER_SPORT_STATS]: (state: IStatisticsState) => {
    return state.sportStatistics
  },
  [STATS_STORE.GETTERS.USER_STATS]: (state: IStatisticsState) => {
    return state.statistics
  },
  [STATS_STORE.GETTERS.STATS_LOADING]: (state: IStatisticsState) => {
    return state.loading
  },
  [STATS_STORE.GETTERS.TOTAL_WORKOUTS]: (state: IStatisticsState) => {
    return state.totalWorkouts
  },
}
