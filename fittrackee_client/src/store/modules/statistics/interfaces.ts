import { ActionContext } from 'vuex'

import { STATS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/interfaces'
import { IUserStatisticsPayload, TStatisticsFromApi } from '@/types/statistics'

export interface IStatisticsState {
  statistics: TStatisticsFromApi
}

export interface IStatisticsActions {
  [STATS_STORE.ACTIONS.GET_USER_STATS](
    context: ActionContext<IStatisticsState, IRootState>,
    payload: IUserStatisticsPayload
  ): void
}

export interface IStatisticsGetters {
  [STATS_STORE.GETTERS.USER_STATS](state: IStatisticsState): TStatisticsFromApi
}
