import type { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import { STATS_STORE, ROOT_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type {
  IStatisticsActions,
  IStatisticsState,
} from '@/store/modules/statistics/types'
import type {
  IUserSportStatisticsPayload,
  IUserStatisticsPayload,
} from '@/types/statistics'
import { handleError } from '@/utils'

export const actions: ActionTree<IStatisticsState, IRootState> &
  IStatisticsActions = {
  [STATS_STORE.ACTIONS.GET_USER_STATS](
    context: ActionContext<IStatisticsState, IRootState>,
    payload: IUserStatisticsPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get(`stats/${payload.username}/by_time`, {
        params: payload.params,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            STATS_STORE.MUTATIONS.UPDATE_USER_STATS,
            res.data.data.statistics
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [STATS_STORE.ACTIONS.GET_USER_SPORT_STATS](
    context: ActionContext<IStatisticsState, IRootState>,
    payload: IUserSportStatisticsPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(STATS_STORE.MUTATIONS.UPDATE_STATS_LOADING, true)
    authApi
      .get(`stats/${payload.username}/by_sport`, {
        params: { sport_id: payload.sportId },
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            STATS_STORE.MUTATIONS.UPDATE_USER_SPORT_STATS,
            res.data.data.statistics
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(STATS_STORE.MUTATIONS.UPDATE_STATS_LOADING, false)
      )
  },
}
