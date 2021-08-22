import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import api from '@/api/defaultApi'
import router from '@/router'
import { ROOT_STORE, SPORTS_STORE, USER_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IUserActions, IUserState } from '@/store/modules/user/types'
import { ILoginOrRegisterData } from '@/types/user'
import { handleError } from '@/utils'

export const actions: ActionTree<IUserState, IRootState> & IUserActions = {
  [USER_STORE.ACTIONS.CHECK_AUTH_USER](
    context: ActionContext<IUserState, IRootState>
  ): void {
    if (
      window.localStorage.authToken &&
      !context.getters[USER_STORE.GETTERS.IS_AUTHENTICATED]
    ) {
      context.commit(
        USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN,
        window.localStorage.authToken
      )
      context.dispatch(USER_STORE.ACTIONS.GET_USER_PROFILE)
    }
  },
  [USER_STORE.ACTIONS.GET_USER_PROFILE](
    context: ActionContext<IUserState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('auth/profile')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE,
            res.data.data
          )
          context.dispatch(SPORTS_STORE.ACTIONS.GET_SPORTS)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [USER_STORE.ACTIONS.LOGIN_OR_REGISTER](
    context: ActionContext<IUserState, IRootState>,
    data: ILoginOrRegisterData
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    api
      .post(`/auth/${data.actionType}`, data.formData)
      .then((res) => {
        if (res.data.status === 'success') {
          const token = res.data.auth_token
          window.localStorage.setItem('authToken', token)
          context.commit(USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN, token)
          context
            .dispatch(USER_STORE.ACTIONS.GET_USER_PROFILE)
            .then(() => router.push('/'))
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [USER_STORE.ACTIONS.LOGOUT](
    context: ActionContext<IUserState, IRootState>
  ): void {
    localStorage.removeItem('authToken')
    context.commit(USER_STORE.MUTATIONS.CLEAR_AUTH_USER_TOKEN)
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    router.push('/login')
  },
}
