import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import { STATS_STORE, ROOT_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import {
  IStatisticsActions,
  IStatisticsState,
} from '@/store/modules/statistics/types'
import { IUserStatisticsPayload } from '@/types/statistics'
import { handleError } from '@/utils'

export const actions: ActionTree<IStatisticsState, IRootState> &
  IStatisticsActions = {
  [STATS_STORE.ACTIONS.GET_USER_STATS](
    context: ActionContext<IStatisticsState, IRootState>,
    payload: IUserStatisticsPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get(`stats/${payload.username}/${payload.filterType}`, {
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
}
