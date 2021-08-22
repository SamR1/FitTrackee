import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import { ROOT_STORE } from '@/store/constants'
import { IRootActions, IRootState } from '@/store/modules/root/types'
import { handleError } from '@/utils'

export const actions: ActionTree<IRootState, IRootState> & IRootActions = {
  [ROOT_STORE.ACTIONS.GET_APPLICATION_CONFIG](
    context: ActionContext<IRootState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_LOADING, true)
    authApi
      .get('config')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_CONFIG,
            res.data.data
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_LOADING, false)
      )
  },
}
