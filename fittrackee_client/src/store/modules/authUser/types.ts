import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { AUTH_USER_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import {
  IAuthUserProfile,
  ILoginOrRegisterData,
  IUserDeletionPayload,
  IUserPasswordPayload,
  IUserPasswordResetPayload,
  IUserPayload,
  IUserPicturePayload,
  IUserPreferencesPayload,
  IUserSportPreferencesPayload,
  IUserAccountPayload,
  IUserEmailUpdatePayload,
} from '@/types/user'

export interface IAuthUserState {
  authToken: string | null
  authUserProfile: IAuthUserProfile
  isSuccess: boolean
  loading: boolean
}

export interface IAuthUserActions {
  [AUTH_USER_STORE.ACTIONS.CHECK_AUTH_USER](
    context: ActionContext<IAuthUserState, IRootState>
  ): void

  [AUTH_USER_STORE.ACTIONS.CONFIRM_EMAIL](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserEmailUpdatePayload
  ): void

  [AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE](
    context: ActionContext<IAuthUserState, IRootState>
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
    payload: IUserPasswordPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.RESET_USER_PASSWORD](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserPasswordResetPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.RESET_USER_SPORT_PREFERENCES](
    context: ActionContext<IAuthUserState, IRootState>,
    sportId: number
  ): void

  [AUTH_USER_STORE.ACTIONS.DELETE_ACCOUNT](
    context: ActionContext<IAuthUserState, IRootState>,
    payload: IUserDeletionPayload
  ): void

  [AUTH_USER_STORE.ACTIONS.DELETE_PICTURE](
    context: ActionContext<IAuthUserState, IRootState>
  ): void
}

export interface IAuthUserGetters {
  [AUTH_USER_STORE.GETTERS.AUTH_TOKEN](state: IAuthUserState): string | null

  [AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE](
    state: IAuthUserState
  ): IAuthUserProfile

  [AUTH_USER_STORE.GETTERS.IS_ADMIN](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.IS_SUCCESS](state: IAuthUserState): boolean

  [AUTH_USER_STORE.GETTERS.USER_LOADING](state: IAuthUserState): boolean
}

export type TAuthUserMutations<S = IAuthUserState> = {
  [AUTH_USER_STORE.MUTATIONS.CLEAR_AUTH_USER_TOKEN](state: S): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN](
    state: S,
    authToken: string
  ): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE](
    state: S,
    authUserProfile: IAuthUserProfile
  ): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS](
    state: S,
    isSuccess: boolean
  ): void
  [AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING](
    state: S,
    loading: boolean
  ): void
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
    P extends Parameters<TAuthUserMutations[K]>[1]
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TAuthUserMutations[K]>
}
