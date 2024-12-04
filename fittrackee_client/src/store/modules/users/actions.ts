import type { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import router from '@/router'
import { AUTH_USER_STORE, ROOT_STORE, USERS_STORE } from '@/store/constants'
import type { IAuthUserState } from '@/store/modules/authUser/types'
import type { IRootState } from '@/store/modules/root/types'
import type { IUsersActions, IUsersState } from '@/store/modules/users/types'
import type {
  IAdminUserPayload,
  IUserDeletionPayload,
  IUserRelationshipActionPayload,
  IUserRelationshipsPayload,
  TUsersPayload,
} from '@/types/user'
import { handleError } from '@/utils'

const ACCOUNT_REGEX = /^@([\w_\-.]+)@([\w_\-.]+\.[a-z]{2,})$/g

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

const getUsers = (
  context:
    | ActionContext<IAuthUserState, IRootState>
    | ActionContext<IUsersState, IRootState>,
  payload: TUsersPayload,
  forAdmin = false
): void => {
  context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING, true)
  const isRemote = payload.q && payload.q.match(ACCOUNT_REGEX) ? '/remote' : ''
  if (forAdmin) {
    payload.with_inactive = 'true'
    payload.with_hidden = 'true'
    payload.with_suspended = 'true'
  }
  authApi
    .get(`users${isRemote}`, { params: payload })
    .then((res) => {
      if (res.data.status === 'success') {
        context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS, res.data.data.users)
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
  [USERS_STORE.ACTIONS.EMPTY_RELATIONSHIPS](
    context: ActionContext<IUsersState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(USERS_STORE.MUTATIONS.UPDATE_USER_RELATIONSHIPS, [])
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
  [USERS_STORE.ACTIONS.GET_USER_SANCTIONS](
    context: ActionContext<IUsersState, IRootState>,
    payload: TUsersPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS_LOADING, true)
    const { username, ...params } = payload
    authApi
      .get(`users/${username}/sanctions`, { params })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS,
            res.data.data.sanctions
          )
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS_PAGINATION,
            res.data.pagination
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(
          USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS_LOADING,
          false
        )
      )
  },
  [USERS_STORE.ACTIONS.GET_USERS](
    context: ActionContext<IUsersState, IRootState>,
    payload: TUsersPayload
  ): void {
    getUsers(context, payload, false)
  },
  [USERS_STORE.ACTIONS.GET_USERS_FOR_ADMIN](
    context: ActionContext<IUsersState, IRootState>,
    payload: TUsersPayload
  ): void {
    getUsers(context, payload, true)
  },
  [USERS_STORE.ACTIONS.UPDATE_USER](
    context: ActionContext<IUsersState, IRootState>,
    payload: IAdminUserPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    const data: Record<string, boolean | string | number | undefined> = {}
    if (payload.role !== undefined) {
      data.role = payload.role
    }
    if (payload.resetPassword) {
      data.reset_password = payload.resetPassword
    }
    if ('activate' in payload && payload.activate !== undefined) {
      data.activate = payload.activate
    }
    if (payload.new_email !== undefined) {
      data.new_email = payload.new_email
    }
    authApi
      .patch(`users/${payload.username}`, data)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS,
            res.data.data.users[0]
          )
          if (payload.resetPassword || payload.new_email || payload.role) {
            context.commit(USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS, true)
          }
          if (payload.activate || payload.new_email) {
            context.commit(
              USERS_STORE.MUTATIONS.UPDATE_USER,
              res.data.data.users[0]
            )
          }
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
    payload: IUserRelationshipActionPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING, true)
    authApi
      .post(`users/${payload.username}/${payload.action}`)
      .then((res) => {
        if (res.data.status === 'success') {
          authApi.get(`users/${payload.username}`).then((res) => {
            if (res.data.status === 'success') {
              if (payload.from === 'blocked-users') {
                context.dispatch(
                  AUTH_USER_STORE.ACTIONS.GET_BLOCKED_USERS,
                  payload.payload
                )
                return
              }
              context.commit(
                payload.from === 'userInfos'
                  ? USERS_STORE.MUTATIONS.UPDATE_USER
                  : payload.from === 'userCard'
                    ? USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS
                    : USERS_STORE.MUTATIONS.UPDATE_USER_IN_RELATIONSHIPS,
                res.data.data.users[0]
              )
              context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE)
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
  [USERS_STORE.ACTIONS.GET_RELATIONSHIPS](
    context: ActionContext<IUsersState, IRootState>,
    payload: IUserRelationshipsPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING, true)
    authApi
      .get(`users/${payload.username}/${payload.relationship}`, {
        params: { page: payload.page },
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USER_RELATIONSHIPS,
            res.data.data[payload.relationship]
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
