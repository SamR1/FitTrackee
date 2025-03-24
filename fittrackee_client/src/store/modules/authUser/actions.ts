import type { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import api from '@/api/defaultApi'
import router from '@/router'
import store from '@/store'
import {
  AUTH_USER_STORE,
  EQUIPMENTS_STORE,
  NOTIFICATIONS_STORE,
  ROOT_STORE,
  SPORTS_STORE,
  STATS_STORE,
  USERS_STORE,
  WORKOUTS_STORE,
} from '@/store/constants'
import type {
  IAuthUserActions,
  IAuthUserState,
} from '@/store/modules/authUser/types'
import type { IRootState } from '@/store/modules/root/types'
import { deleteUserAccount } from '@/store/modules/users/actions'
import type { IPagePayload } from '@/types/api'
import type { TNotificationPreferences } from '@/types/notifications.ts'
import type {
  IFollowRequestsActionPayload,
  ILoginOrRegisterData,
  IUserAccountPayload,
  IUserDeletionPayload,
  IUserAccountUpdatePayload,
  IUserEmailPayload,
  IUserPasswordResetPayload,
  IUserPayload,
  IUserPicturePayload,
  IUserPreferencesPayload,
  IUserSportPreferencesPayload,
  IUserSportPreferencesResetPayload,
  IUserAppealPayload,
  IGetUserProfilePayload,
} from '@/types/user'
import { handleError } from '@/utils'

const removeAuthUserData = (
  context: ActionContext<IAuthUserState, IRootState>
) => {
  localStorage.removeItem('authToken')
  context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  context.commit(STATS_STORE.MUTATIONS.EMPTY_USER_STATS)
  context.commit(STATS_STORE.MUTATIONS.EMPTY_USER_SPORT_STATS)
  context.commit(AUTH_USER_STORE.MUTATIONS.CLEAR_AUTH_USER_TOKEN)
  context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_FOLLOW_REQUESTS, [])
  context.commit(USERS_STORE.MUTATIONS.UPDATE_USERS, [])
  context.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUTS)
  context.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
  router.push('/login')
}

export const actions: ActionTree<IAuthUserState, IRootState> &
  IAuthUserActions = {
  [AUTH_USER_STORE.ACTIONS.CHECK_AUTH_USER](
    context: ActionContext<IAuthUserState, IRootState>
  ): void {
    if (
      window.localStorage.authToken &&
      !context.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED]
    ) {
      context.commit(
        AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN,
        window.localStorage.authToken
      )
      context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {
        updateUI: true,
      })
    }
    // after logout in another tab
    if (
      !window.localStorage.authToken &&
      context.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED]
    ) {
      removeAuthUserData(context)
    }
  },
  [AUTH_USER_STORE.ACTIONS.CONFIRM_ACCOUNT](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserAccountUpdatePayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    api
      .post('auth/account/confirm', { token: payload.token })
      .then((res) => {
        if (res.data.status === 'success') {
          const token = res.data.auth_token
          window.localStorage.setItem('authToken', token)
          context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN, token)
          context
            .dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
            .then(() => router.push('/'))
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        handleError(context, error)
      })
  },
  [AUTH_USER_STORE.ACTIONS.CONFIRM_EMAIL](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserAccountUpdatePayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    api
      .post('/auth/email/update', { token: payload.token })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, true)
          if (payload.refreshUser) {
            context
              .dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
              .then(() => {
                return router.push('/profile/edit/account')
              })
          }
          router.push('/profile/edit/account')
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        handleError(context, error)
      })
  },
  [AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IGetUserProfilePayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('auth/profile')
      .then((res) => {
        if (res.data.status === 'success') {
          const profileNotLoaded =
            context.getters[AUTH_USER_STORE.GETTERS.IS_PROFILE_NOT_LOADED]
          context.commit(
            AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE,
            res.data.data
          )
          if (!res.data.data.accepted_privacy_policy) {
            // refresh privacy policy
            context.dispatch(ROOT_STORE.ACTIONS.GET_APPLICATION_PRIVACY_POLICY)
          }
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS,
            res.data.data
          )
          if (profileNotLoaded || payload.updateUI) {
            if (res.data.data.language) {
              context.dispatch(
                ROOT_STORE.ACTIONS.UPDATE_APPLICATION_LANGUAGE,
                res.data.data.language
              )
            }
            context.commit(
              ROOT_STORE.MUTATIONS.UPDATE_DARK_MODE,
              res.data.data.use_dark_mode
            )
          }

          if (!('light' in payload) || !payload.light) {
            context.commit(
              ROOT_STORE.MUTATIONS.UPDATE_DISPLAY_OPTIONS,
              res.data.data
            )
            context.dispatch(SPORTS_STORE.ACTIONS.GET_SPORTS)
            context.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENTS)
            context.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENT_TYPES)
          }

          if (res.data.data.suspended_at === null) {
            store.dispatch(NOTIFICATIONS_STORE.ACTIONS.GET_UNREAD_STATUS)
          } else if (
            !router.currentRoute.value.path.startsWith('/profile') &&
            !router.currentRoute.value.meta.allowedToSuspendedUser
          ) {
            router.push('/profile')
          }
        } else {
          handleError(context, null)
          removeAuthUserData(context)
        }
      })
      .catch((error) => {
        if (error.message !== 'canceled') {
          handleError(context, error)
          removeAuthUserData(context)
        }
      })
  },
  [AUTH_USER_STORE.ACTIONS.GET_ACCOUNT_SUSPENSION](
    context: ActionContext<IAuthUserState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    authApi
      .get('auth/account/suspension')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.SET_ACCOUNT_SUSPENSION,
            res.data.user_suspension
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        if (error.message !== 'canceled') {
          handleError(context, error)
        }
      })
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.GET_FOLLOW_REQUESTS](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IPagePayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    authApi
      .get('follow-requests', { params: payload })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.UPDATE_FOLLOW_REQUESTS,
            res.data.data.follow_requests
          )
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USERS_PAGINATION,
            res.data.pagination
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        handleError(context, error)
      })
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.LOGIN_OR_REGISTER](
    context: ActionContext<IAuthUserState, IRootState>,
    data: ILoginOrRegisterData
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(
      AUTH_USER_STORE.MUTATIONS.UPDATE_IS_REGISTRATION_SUCCESS,
      false
    )
    api
      .post(`/auth/${data.actionType}`, data.formData)
      .then((res) => {
        if (res.data.status === 'success') {
          if (data.actionType === 'login') {
            const token = res.data.auth_token
            window.localStorage.setItem('authToken', token)
            context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN, token)
            context
              .dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {
                updateUI: true,
              })
              .then(() =>
                router.push(
                  typeof data.redirectUrl === 'string' ? data.redirectUrl : '/'
                )
              )
          } else {
            router
              .push('/login')
              .then(() =>
                context.commit(
                  AUTH_USER_STORE.MUTATIONS.UPDATE_IS_REGISTRATION_SUCCESS,
                  true
                )
              )
          }
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [AUTH_USER_STORE.ACTIONS.LOGOUT](
    context: ActionContext<IAuthUserState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .post('auth/logout')
      .then((res) => {
        if (res.data.status === 'success') {
          removeAuthUserData(context)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [AUTH_USER_STORE.ACTIONS.APPEAL](
    context: ActionContext<IAuthUserState, IRootState>,
    appealPayload: IUserAppealPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    const url =
      appealPayload.actionType === 'user_suspension'
        ? 'auth/account/suspension/appeal'
        : `auth/account/sanctions/${appealPayload.actionId}/appeal`
    authApi
      .post(url, { text: appealPayload.text })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, true)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        if (error.message !== 'canceled') {
          handleError(context, error)
        }
      })
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.UPDATE_FOLLOW_REQUESTS](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IFollowRequestsActionPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .post(`follow-requests/${payload.username}/${payload.action}`)
      .then((res) => {
        if (res.data.status === 'success') {
          if (payload.getFollowRequests) {
            context
              .dispatch(AUTH_USER_STORE.ACTIONS.GET_FOLLOW_REQUESTS)
              .then(() =>
                context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
              )
          }
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_PROFILE](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    authApi
      .post('auth/profile/edit', payload)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE,
            res.data.data
          )
          router.push('/profile')
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_ACCOUNT](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserAccountPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    authApi
      .patch('auth/profile/edit/account', payload)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE,
            res.data.data
          )
          context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, true)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_PREFERENCES](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserPreferencesPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    authApi
      .post('auth/profile/edit/preferences', payload)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE,
            res.data.data
          )
          context.commit(
            ROOT_STORE.MUTATIONS.UPDATE_DISPLAY_OPTIONS,
            res.data.data
          )
          context.commit(
            ROOT_STORE.MUTATIONS.UPDATE_DARK_MODE,
            res.data.data.use_dark_mode
          )
          context
            .dispatch(
              ROOT_STORE.ACTIONS.UPDATE_APPLICATION_LANGUAGE,
              res.data.data.language
            )
            .then(() => router.push('/profile/preferences'))
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.RESET_USER_SPORT_PREFERENCES](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserSportPreferencesResetPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    authApi
      .delete(`auth/profile/reset/sports/${payload.sportId}`)
      .then((res) => {
        if (res.status === 204) {
          context.dispatch(SPORTS_STORE.ACTIONS.GET_SPORTS)
          if (payload.fromSport) {
            router.push(`/profile/sports/${payload.sportId}`)
          }
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        handleError(context, error)
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      })
  },
  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_SPORT_PREFERENCES](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserSportPreferencesPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    const { fromSport, ...data } = payload
    authApi
      .post('auth/profile/edit/sports', data)
      .then((res) => {
        if (res.data.status === 'success') {
          context.dispatch(SPORTS_STORE.ACTIONS.GET_SPORTS)
          if (fromSport) {
            router.push(`/profile/sports/${data.sport_id}`)
          }
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        handleError(context, error)
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      })
  },
  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_PICTURE](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserPicturePayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    if (!payload.picture) {
      throw new Error('No file part')
    }
    const form = new FormData()
    form.append('file', payload.picture)
    authApi
      .post('auth/picture', form, {
        headers: {
          'content-type': 'multipart/form-data',
        },
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context
            .dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
            .then(() => router.push('/profile'))
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.DELETE_ACCOUNT](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserDeletionPayload
  ): void {
    deleteUserAccount(context, payload)
  },
  [AUTH_USER_STORE.ACTIONS.DELETE_PICTURE](
    context: ActionContext<IAuthUserState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    authApi
      .delete(`auth/picture`)
      .then((res) => {
        if (res.status === 204) {
          context
            .dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
            .then(() => router.push('/profile'))
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.SEND_PASSWORD_RESET_REQUEST](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserEmailPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    api
      .post('auth/password/reset-request', payload)
      .then((res) => {
        if (res.data.status === 'success') {
          router.push('/password-reset/sent')
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [AUTH_USER_STORE.ACTIONS.RESEND_ACCOUNT_CONFIRMATION_EMAIL](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserEmailPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    api
      .post('auth/account/resend-confirmation', payload)
      .then((res) => {
        if (res.data.status === 'success') {
          router.push('/account-confirmation/email-sent')
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [AUTH_USER_STORE.ACTIONS.RESET_USER_PASSWORD](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserPasswordResetPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    api
      .post('auth/password/update', payload)
      .then((res) => {
        if (res.data.status === 'success') {
          router.push('/password-reset/password-updated')
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [AUTH_USER_STORE.ACTIONS.ACCEPT_PRIVACY_POLICY](
    context: ActionContext<IAuthUserState, IRootState>,
    acceptedPolicy: boolean
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .post('auth/account/privacy-policy', {
        accepted_policy: acceptedPolicy,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context
            .dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
            .then(() => router.push('/profile'))
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [AUTH_USER_STORE.ACTIONS.REQUEST_DATA_EXPORT](
    context: ActionContext<IAuthUserState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .post('auth/account/export/request')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.SET_EXPORT_REQUEST,
            res.data.request
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [AUTH_USER_STORE.ACTIONS.GET_REQUEST_DATA_EXPORT](
    context: ActionContext<IAuthUserState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('auth/account/export')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.SET_EXPORT_REQUEST,
            res.data.request
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [AUTH_USER_STORE.ACTIONS.GET_BLOCKED_USERS](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IPagePayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    authApi
      .get('auth/blocked-users', { params: payload })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.UPDATE_BLOCKED_USERS,
            res.data.blocked_users
          )
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USERS_PAGINATION,
            res.data.pagination
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        handleError(context, error)
      })
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.GET_USER_SANCTION](
    context: ActionContext<IAuthUserState, IRootState>,
    actionId: string
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    authApi
      .get(`auth/account/sanctions/${actionId}`)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.SET_USER_SANCTION,
            res.data.sanction
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        if (error.message !== 'canceled') {
          handleError(context, error)
        }
      })
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_NOTIFICATIONS_PREFERENCES](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: TNotificationPreferences
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, true)
    authApi
      .post('auth/profile/edit/notifications', payload)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE,
            res.data.data
          )
          router.push('/profile/notifications')
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
      )
  },
  [AUTH_USER_STORE.ACTIONS.GET_TIMEZONES](
    context: ActionContext<IAuthUserState, IRootState>
  ): void {
    const timezoneError = 'error when getting timezones'
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('auth/timezones')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            AUTH_USER_STORE.MUTATIONS.SET_TIMEZONES,
            res.data.timezones
          )
        } else {
          handleError(context, null, timezoneError)
        }
      })
      .catch(() => {
        handleError(context, null, timezoneError)
      })
  },
}
