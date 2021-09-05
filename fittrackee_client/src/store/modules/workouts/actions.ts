import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import {
  IWorkoutsActions,
  IWorkoutsState,
} from '@/store/modules/workouts/types'
import { IWorkoutsPayload } from '@/types/workouts'
import { handleError } from '@/utils'

export const actions: ActionTree<IWorkoutsState, IRootState> &
  IWorkoutsActions = {
  [WORKOUTS_STORE.ACTIONS.GET_CALENDAR_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutsPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('workouts', {
        params: payload,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_CALENDAR_WORKOUTS,
            res.data.data.statistics
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
}
