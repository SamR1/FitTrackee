import type { Module } from 'vuex'

import type { IRootState } from '@/store/modules/root/types'
import { actions } from '@/store/modules/statistics/actions'
import { getters } from '@/store/modules/statistics/getters'
import { mutations } from '@/store/modules/statistics/mutations'
import { statisticsState } from '@/store/modules/statistics/state'
import type { IStatisticsState } from '@/store/modules/statistics/types'

const statistics: Module<IStatisticsState, IRootState> = {
  state: statisticsState,
  actions,
  getters,
  mutations,
}

export default statistics
