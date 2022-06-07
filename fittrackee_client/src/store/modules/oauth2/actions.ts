import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import router from '@/router'
import { OAUTH2_STORE, ROOT_STORE } from '@/store/constants'
import { IOAuth2Actions, IOAuth2State } from '@/store/modules/oauth2/types'
import { IRootState } from '@/store/modules/root/types'
import {
  IOauth2ClientsPayload,
  IOAuth2ClientPayload,
  IOAuth2ClientAuthorizePayload,
} from '@/types/oauth'
import { handleError } from '@/utils'

const get_client = (
  context: ActionContext<IOAuth2State, IRootState>,
  url: string
) => {
  context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  authApi
    .get(url)
    .then((res) => {
      if (res.data.status === 'success') {
        context.commit(OAUTH2_STORE.MUTATIONS.SET_CLIENT, res.data.data.client)
      } else {
        handleError(context, null)
      }
    })
    .catch((error) => handleError(context, error))
}

export const actions: ActionTree<IOAuth2State, IRootState> & IOAuth2Actions = {
  [OAUTH2_STORE.ACTIONS.AUTHORIZE_CLIENT](
    context: ActionContext<IOAuth2State, IRootState>,
    payload: IOAuth2ClientAuthorizePayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    const form = new FormData()
    form.set('client_id', payload.client_id)
    form.set('response_type', payload.response_type)
    form.set('scope', payload.scope)
    form.set('confirm', 'true')
    if (payload.state) {
      form.set('state', payload.state)
    }

    authApi
      .post('oauth/authorize', form, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then((res) => {
        if (res.status == 200 && res.data.redirect_url) {
          window.location.href = res.data.redirect_url
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [OAUTH2_STORE.ACTIONS.CREATE_CLIENT](
    context: ActionContext<IOAuth2State, IRootState>,
    payload: IOAuth2ClientPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .post('oauth/apps', payload)
      .then((res) => {
        if (res.data.status === 'created') {
          context.commit(
            OAUTH2_STORE.MUTATIONS.SET_CLIENT,
            res.data.data.client
          )
          router.push(`/profile/apps/${res.data.data.client.id}/created`)
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
  [OAUTH2_STORE.ACTIONS.GET_CLIENT_BY_CLIENT_ID](
    context: ActionContext<IOAuth2State, IRootState>,
    client_id: string
  ): void {
    get_client(context, `oauth/apps/${client_id}`)
  },
  [OAUTH2_STORE.ACTIONS.GET_CLIENT_BY_ID](
    context: ActionContext<IOAuth2State, IRootState>,
    id: number
  ): void {
    get_client(context, `oauth/apps/${id}/by_id`)
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
