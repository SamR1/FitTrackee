import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import router from '@/router'
import { AUTH_USER_STORE, ROOT_STORE, USERS_STORE } from '@/store/constants'
import { IAuthUserState } from '@/store/modules/authUser/types'
import { IRootState } from '@/store/modules/root/types'
import { IUsersActions, IUsersState } from '@/store/modules/users/types'
import {
  IAdminUserPayload,
  IUserDeletionPayload,
  IUserRelationshipPayload,
  TUsersPayload,
} from '@/types/user'
import { handleError } from '@/utils'

export const deleteUserAccount = (
  context:
    | ActionContext<IAuthUserState, IRootState>
    | ActionContext<IUsersState, IRootState>,
  payload: IUserDeletionPayload
): void => {
  context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  authApi
    .delete(`users/${payload.username}`)
    .then((res) => {
      if (res.status === 204) {
        if (payload.fromAdmin) {
          router.push('/admin/users')
        } else {
          context
            .dispatch(AUTH_USER_STORE.ACTIONS.LOGOUT)
            .then(() => router.push('/'))
        }
      } else {
        handleError(context, null)
      }
    })
    .catch((error) => handleError(context, error))
}

export const actions: ActionTree<IUsersState, IRootState> & IUsersActions = {
  [USERS_STORE.ACTIONS.EMPTY_USER](
    context: ActionContext<IUsersState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(USERS_STORE.MUTATIONS.UPDATE_USER, {})
  },
  [USERS_STORE.ACTIONS.EMPTY_USERS](
    context: ActionContext<IUsersState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS, [])
    context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_PAGINATION, {})
  },
  [USERS_STORE.ACTIONS.GET_USER](
    context: ActionContext<IUsersState, IRootState>,
    username: string
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING, true)
    authApi
      .get(`users/${username}`)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USER,
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
  [USERS_STORE.ACTIONS.GET_USERS](
    context: ActionContext<IUsersState, IRootState>,
    payload: TUsersPayload
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
  [USERS_STORE.ACTIONS.UPDATE_RELATIONSHIP](
    context: ActionContext<IUsersState, IRootState>,
    payload: IUserRelationshipPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING, true)
    authApi
      .post(`users/${payload.username}/${payload.action}`)
      .then((res) => {
        if (res.data.status === 'success') {
          authApi.get(`users/${payload.username}`).then((res) => {
            if (res.data.status === 'success') {
              context.commit(
                payload.fromUserInfos
                  ? USERS_STORE.MUTATIONS.UPDATE_USER
                  : USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS,
                res.data.data.users[0]
              )
            } else {
              handleError(context, null)
            }
          })
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING, false)
      )
  },
  [USERS_STORE.ACTIONS.DELETE_USER_ACCOUNT](
    context: ActionContext<IUsersState, IRootState>,
    payload: IUserDeletionPayload
  ): void {
    deleteUserAccount(context, {
      username: payload.username,
      fromAdmin: true,
    })
  },
}
