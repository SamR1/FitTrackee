import type { GetterTree } from 'vuex'

import { STATS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type {
  IStatisticsGetters,
  IStatisticsState,
} from '@/store/modules/statistics/types'

export const getters: GetterTree<IStatisticsState, IRootState> &
  IStatisticsGetters = {
  [STATS_STORE.GETTERS.USER_STATS]: (state: IStatisticsState) => {
    return state.statistics
  },
}
