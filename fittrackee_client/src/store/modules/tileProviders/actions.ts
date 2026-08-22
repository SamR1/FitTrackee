import type { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import { ROOT_STORE, TILE_PROVIDERS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type {
  ITileProvidersActions,
  ITileProvidersState,
} from '@/store/modules/tileProviders/types'
import type { ITileProviderPayload } from '@/types/tileProviders.ts'
import { handleError } from '@/utils'

export const actions: ActionTree<ITileProvidersState, IRootState> &
  ITileProvidersActions = {
  [TILE_PROVIDERS_STORE.ACTIONS.GET_TILE_PROVIDERS](
    context: ActionContext<ITileProvidersState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('tile-providers')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            TILE_PROVIDERS_STORE.MUTATIONS.SET_TILE_PROVIDER,
            res.data.data.tile_providers
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [TILE_PROVIDERS_STORE.ACTIONS.UPDATE_TILE_PROVIDER](
    context: ActionContext<ITileProvidersState, IRootState>,
    payload: ITileProviderPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .patch(`tile-providers/${payload.id}`, {
        default: payload.default,
        enabled: payload.enabled,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context.dispatch(TILE_PROVIDERS_STORE.ACTIONS.GET_TILE_PROVIDERS)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
}
