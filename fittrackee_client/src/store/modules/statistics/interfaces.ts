import { ActionContext } from 'vuex'

import { STATS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/interfaces'
import { IUserStatisticsPayload, TStatistics } from '@/types/statistics'

export interface IStatisticsState {
  statistics: TStatistics
}

export interface IStatisticsActions {
  [STATS_STORE.ACTIONS.GET_USER_STATS](
    context: ActionContext<IStatisticsState, IRootState>,
    payload: IUserStatisticsPayload
  ): void
}

export interface IStatisticsGetters {
  [STATS_STORE.GETTERS.USER_STATS](state: IStatisticsState): TStatistics
}
