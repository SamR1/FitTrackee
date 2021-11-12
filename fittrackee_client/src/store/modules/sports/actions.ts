import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import { AUTH_USER_STORE, ROOT_STORE, SPORTS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { ISportsActions, ISportsState } from '@/store/modules/sports/types'
import { ISportPayload } from '@/types/sports'
import { handleError } from '@/utils'

export const actions: ActionTree<ISportsState, IRootState> & ISportsActions = {
  [SPORTS_STORE.ACTIONS.GET_SPORTS](
    context: ActionContext<ISportsState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('sports')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            SPORTS_STORE.MUTATIONS.SET_SPORTS,
            res.data.data.sports
          )
          context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [SPORTS_STORE.ACTIONS.UPDATE_SPORTS](
    context: ActionContext<ISportsState, IRootState>,
    payload: ISportPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .patch(`sports/${payload.id}`, { is_active: payload.isActive })
      .then((res) => {
        if (res.data.status === 'success') {
          context.dispatch(SPORTS_STORE.ACTIONS.GET_SPORTS)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
}
