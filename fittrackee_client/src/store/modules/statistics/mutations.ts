import { MutationTree } from 'vuex'

import { STATS_STORE } from '@/store/constants'
import { IStatisticsState } from '@/store/modules/statistics/interfaces'
import { TStatisticsMutations } from '@/store/modules/statistics/types'
import { TStatisticsFromApi } from '@/types/statistics'

export const mutations: MutationTree<IStatisticsState> & TStatisticsMutations =
  {
    [STATS_STORE.MUTATIONS.UPDATE_USER_STATS](
      state: IStatisticsState,
      statistics: TStatisticsFromApi
    ) {
      state.statistics = statistics
    },
  }
