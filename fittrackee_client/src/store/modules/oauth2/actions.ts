import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import router from '@/router'
import { OAUTH2_STORE, ROOT_STORE } from '@/store/constants'
import { IOAuth2Actions, IOAuth2State } from '@/store/modules/oauth2/types'
import { IRootState } from '@/store/modules/root/types'
import { IOauth2ClientsPayload, IOAuth2ClientPayload } from '@/types/oauth'
import { handleError } from '@/utils'

export const actions: ActionTree<IOAuth2State, IRootState> & IOAuth2Actions = {
  [OAUTH2_STORE.ACTIONS.CREATE_CLIENT](
    context: ActionContext<IOAuth2State, IRootState>,
    payload: IOAuth2ClientPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .post('oauth/apps', payload)
      .then((res) => {
        if (res.data.status === 'created') {
          context
            .dispatch(OAUTH2_STORE.ACTIONS.GET_CLIENTS)
            .then(() => router.push('/profile/apps'))
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [OAUTH2_STORE.ACTIONS.DELETE_CLIENT](
    context: ActionContext<IOAuth2State, IRootState>,
    id: number
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .delete(`oauth/apps/${id}`)
      .then((res) => {
        if (res.status === 204) {
          context
            .dispatch(OAUTH2_STORE.ACTIONS.GET_CLIENTS)
            .then(() => router.push('/profile/apps'))
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [OAUTH2_STORE.ACTIONS.GET_CLIENT](
    context: ActionContext<IOAuth2State, IRootState>,
    id: string
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get(`oauth/apps/${id}`)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            OAUTH2_STORE.MUTATIONS.SET_CLIENT,
            res.data.data.client
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [OAUTH2_STORE.ACTIONS.GET_CLIENTS](
    context: ActionContext<IOAuth2State, IRootState>,
    payload: IOauth2ClientsPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('oauth/apps', {
        params: payload,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            OAUTH2_STORE.MUTATIONS.SET_CLIENTS,
            res.data.data.clients
          )
          context.commit(
            OAUTH2_STORE.MUTATIONS.SET_CLIENTS_PAGINATION,
            res.data.pagination
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
}
