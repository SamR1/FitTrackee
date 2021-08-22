import { GetterTree } from 'vuex'

import { STATS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import {
  IStatisticsGetters,
  IStatisticsState,
} from '@/store/modules/statistics/types'

export const getters: GetterTree<IStatisticsState, IRootState> &
  IStatisticsGetters = {
  [STATS_STORE.GETTERS.USER_STATS]: (state: IStatisticsState) => {
    return state.statistics
  },
}
