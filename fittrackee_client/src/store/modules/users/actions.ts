import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import { ROOT_STORE, USERS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IUsersActions, IUsersState } from '@/store/modules/users/types'
import { TPaginationPayload } from '@/types/api'
import { IAdminUserPayload } from '@/types/user'
import { handleError } from '@/utils'

export const actions: ActionTree<IUsersState, IRootState> & IUsersActions = {
  [USERS_STORE.ACTIONS.GET_USERS](
    context: ActionContext<IUsersState, IRootState>,
    payload: TPaginationPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING, true)
    authApi
      .get('users', { params: payload })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USERS,
            res.data.data.users
          )
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USERS_PAGINATION,
            res.data.pagination
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING, false)
      )
  },
  [USERS_STORE.ACTIONS.UPDATE_USER](
    context: ActionContext<IUsersState, IRootState>,
    payload: IAdminUserPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .patch(`users/${payload.username}`, { admin: payload.admin })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS,
            res.data.data.users[0]
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING, false)
      )
  },
}
