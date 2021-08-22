import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import { ROOT_STORE, SPORTS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { ISportsActions, ISportsState } from '@/store/modules/sports/types'
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
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
}
