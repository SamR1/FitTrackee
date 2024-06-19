import type { MutationTree } from 'vuex'

import { STATS_STORE } from '@/store/constants'
import type {
  IStatisticsState,
  TStatisticsMutations,
} from '@/store/modules/statistics/types'
import type {
  TSportStatisticsFromApi,
  TStatisticsFromApi,
} from '@/types/statistics'

export const mutations: MutationTree<IStatisticsState> & TStatisticsMutations =
  {
    [STATS_STORE.MUTATIONS.UPDATE_USER_STATS](
      state: IStatisticsState,
      statistics: TStatisticsFromApi
    ) {
      state.statistics = statistics
    },
    [STATS_STORE.MUTATIONS.EMPTY_USER_STATS](state: IStatisticsState) {
      state.statistics = {}
    },
    [STATS_STORE.MUTATIONS.EMPTY_USER_SPORT_STATS](state: IStatisticsState) {
      state.sportStatistics = {}
      state.totalWorkouts = 0
    },
    [STATS_STORE.MUTATIONS.UPDATE_USER_SPORT_STATS](
      state: IStatisticsState,
      sportStatistics: TSportStatisticsFromApi
    ) {
      state.sportStatistics = sportStatistics
    },
    [STATS_STORE.MUTATIONS.UPDATE_STATS_LOADING](
      state: IStatisticsState,
      loading: boolean
    ) {
      state.loading = loading
    },
    [STATS_STORE.MUTATIONS.UPDATE_TOTAL_WORKOUTS](
      state: IStatisticsState,
      totalWorkouts: number
    ) {
      state.totalWorkouts = totalWorkouts
    },
  }
