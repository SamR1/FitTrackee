import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { AUTH_USER_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { IPagePayload } from '@/types/api'
import type { TNotificationPreferences } from '@/types/notifications.ts'
import type {
  IAuthUserProfile,
  IFollowRequestsActionPayload,
  ILoginOrRegisterData,
  IUserDeletionPayload,
  IUserEmailPayload,
  IUserPasswordResetPayload,
  IUserPayload,
  IUserPicturePayload,
  IUserPreferencesPayload,
  IUserSportPreferencesResetPayload,
  IUserProfile,
  IUserSportPreferencesPayload,
  IUserAccountPayload,
  IUserAccountUpdatePayload,
  IExportRequest,
  IUserReportAction,
  IUserAppealPayload,
  IGetUserProfilePayload,
} from '@/types/user'

export interface IAuthUserState {
  authToken: string | null
  authUserProfile: IAuthUserProfile
  isRegistrationSuccess: boolean
  isSuccess: boolean
  loading: boolean
  exportRequest: IExportRequest | null
  followRequests: IUserProfile[]
  blockedUsers: IUserProfile[]
  userReportAction: IUserReportAction
  timezones: string[]
}

export interface IAuthUserActions {
  [AUTH_USER_STORE.ACTIONS.CHECK_AUTH_USER](
    context: ActionContext<IAuthUserState, IRootState>
  ): void

  [AUTH_USER_STORE.ACTIONS.CONFIRM_ACCOUNT](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserAccountUpdatePayload
  ): void

  [AUTH_USER_STORE.ACTIONS.CONFIRM_EMAIL](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserAccountUpdatePayload
  ): void

  [AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IGetUserProfilePayload
  ): void

  [AUTH_USER_STORE.ACTIONS.GET_ACCOUNT_SUSPENSION](
    context: ActionContext<IAuthUserState, IRootState>
  ): void

  [AUTH_USER_STORE.ACTIONS.GET_FOLLOW_REQUESTS](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IPagePayload
  ): void

  [AUTH_USER_STORE.ACTIONS.LOGIN_OR_REGISTER](
    context: ActionContext<IAuthUserState, IRootState>,
    data: ILoginOrRegisterData
  ): void

  [AUTH_USER_STORE.ACTIONS.LOGOUT](
    context: ActionContext<IAuthUserState, IRootState>
  ): void

  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_PROFILE](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.UPDATE_FOLLOW_REQUESTS](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IFollowRequestsActionPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_ACCOUNT](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserAccountPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_PREFERENCES](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserPreferencesPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_SPORT_PREFERENCES](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserSportPreferencesPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_PICTURE](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserPicturePayload
  ): void

  [AUTH_USER_STORE.ACTIONS.SEND_PASSWORD_RESET_REQUEST](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserEmailPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.RESEND_ACCOUNT_CONFIRMATION_EMAIL](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserEmailPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.RESET_USER_PASSWORD](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserPasswordResetPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.RESET_USER_SPORT_PREFERENCES](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserSportPreferencesResetPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.DELETE_ACCOUNT](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserDeletionPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.DELETE_PICTURE](
    context: ActionContext<IAuthUserState, IRootState>
  ): void

  [AUTH_USER_STORE.ACTIONS.ACCEPT_PRIVACY_POLICY](
    context: ActionContext<IAuthUserState, IRootState>,
    acceptedPolicy: boolean
  ): void

  [AUTH_USER_STORE.ACTIONS.REQUEST_DATA_EXPORT](
    context: ActionContext<IAuthUserState, IRootState>
  ): void

  [AUTH_USER_STORE.ACTIONS.GET_REQUEST_DATA_EXPORT](
    context: ActionContext<IAuthUserState, IRootState>
  ): void

  [AUTH_USER_STORE.ACTIONS.GET_BLOCKED_USERS](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IPagePayload
  ): void

  [AUTH_USER_STORE.ACTIONS.APPEAL](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserAppealPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.GET_USER_SANCTION](
    context: ActionContext<IAuthUserState, IRootState>,
    actionId: string
  ): void

  [AUTH_USER_STORE.ACTIONS.UPDATE_USER_NOTIFICATIONS_PREFERENCES](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: TNotificationPreferences
  ): void

  [AUTH_USER_STORE.ACTIONS.GET_TIMEZONES](
    context: ActionContext<IAuthUserState, IRootState>
  ): void
}

export interface IAuthUserGetters {
  [AUTH_USER_STORE.GETTERS.AUTH_TOKEN](state: IAuthUserState): string | null

  [AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE](
    state: IAuthUserState
  ): IAuthUserProfile

  [AUTH_USER_STORE.GETTERS.BLOCKED_USERS](state: IAuthUserState): IUserProfile[]

  [AUTH_USER_STORE.GETTERS.EXPORT_REQUEST](
    state: IAuthUserState
  ): IExportRequest | null

  [AUTH_USER_STORE.GETTERS.FOLLOW_REQUESTS](
    state: IAuthUserState
  ): IUserProfile[]

  [AUTH_USER_STORE.GETTERS.HAS_ADMIN_RIGHTS](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.HAS_MODERATOR_RIGHTS](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.HAS_OWNER_RIGHTS](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.IS_PROFILE_NOT_LOADED](
    state: IAuthUserState
  ): boolean

  [AUTH_USER_STORE.GETTERS.IS_REGISTRATION_SUCCESS](
    state: IAuthUserState
  ): boolean

  [AUTH_USER_STORE.GETTERS.IS_SUCCESS](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.IS_SUSPENDED](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.IS_PROFILE_LOADED](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.USER_LOADING](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.ACCOUNT_SUSPENSION](
    state: IAuthUserState
  ): IUserReportAction

  [AUTH_USER_STORE.GETTERS.USER_SANCTION](
    state: IAuthUserState
  ): IUserReportAction

  [AUTH_USER_STORE.GETTERS.TIMEZONES](state: IAuthUserState): string[]
}

export type TAuthUserMutations<S = IAuthUserState> = {
  [AUTH_USER_STORE.MUTATIONS.CLEAR_AUTH_USER_TOKEN](state: S): void
  [AUTH_USER_STORE.MUTATIONS.SET_EXPORT_REQUEST](
    state: S,
    exportRequest: IExportRequest | null
  ): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN](
    state: S,
    authToken: string
  ): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE](
    state: S,
    authUserProfile: IAuthUserProfile
  ): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_BLOCKED_USERS](
    state: S,
    blockedUsers: IUserProfile[]
  ): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_FOLLOW_REQUESTS](
    state: S,
    followRequests: IUserProfile[]
  ): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS](
    state: S,
    isSuccess: boolean
  ): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING](
    state: S,
    loading: boolean
  ): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_IS_REGISTRATION_SUCCESS](
    state: S,
    loading: boolean
  ): void
  [AUTH_USER_STORE.MUTATIONS.SET_ACCOUNT_SUSPENSION](
    state: S,
    accountSuspension: IUserReportAction
  ): void
  [AUTH_USER_STORE.MUTATIONS.SET_USER_SANCTION](
    state: S,
    sanction: IUserReportAction
  ): void
  [AUTH_USER_STORE.MUTATIONS.SET_TIMEZONES](state: S, timezones: string[]): void
}

export type TAuthUserStoreModule<S = IAuthUserState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IAuthUserActions>(
    key: K,
    payload?: Parameters<IAuthUserActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IAuthUserActions[K]>
} & {
  getters: {
    [K in keyof IAuthUserGetters]: ReturnType<IAuthUserGetters[K]>
  }
} & {
  commit<
    K extends keyof TAuthUserMutations,
    P extends Parameters<TAuthUserMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TAuthUserMutations[K]>
}
