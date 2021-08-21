import { Module } from 'vuex'

import { IRootState } from '@/store/modules/root/interfaces'
import { actions } from '@/store/modules/statistics/actions'
import { getters } from '@/store/modules/statistics/getters'
import { IStatisticsState } from '@/store/modules/statistics/interfaces'
import { mutations } from '@/store/modules/statistics/mutations'
import { statisticsState } from '@/store/modules/statistics/state'

const statistics: Module<IStatisticsState, IRootState> = {
  state: statisticsState,
  actions,
  getters,
  mutations,
}

export default statistics
