import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { USER_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import {
  IUserProfile,
  ILoginOrRegisterData,
  IUserDeletionPayload,
  IUserPasswordPayload,
  IUserPasswordResetPayload,
  IUserPayload,
  IUserPicturePayload,
  IUserPreferencesPayload,
} from '@/types/user'

export interface IUserState {
  authToken: string | null
  authUserProfile: IUserProfile
  loading: boolean
}

export interface IUserActions {
  [USER_STORE.ACTIONS.CHECK_AUTH_USER](
    context: ActionContext<IUserState, IRootState>
  ): void

  [USER_STORE.ACTIONS.GET_USER_PROFILE](
    context: ActionContext<IUserState, IRootState>
  ): void

  [USER_STORE.ACTIONS.LOGIN_OR_REGISTER](
    context: ActionContext<IUserState, IRootState>,
    data: ILoginOrRegisterData
  ): void

  [USER_STORE.ACTIONS.LOGOUT](
    context: ActionContext<IUserState, IRootState>
  ): void

  [USER_STORE.ACTIONS.UPDATE_USER_PROFILE](
    context: ActionContext<IUserState, IRootState>,
    payload: IUserPayload
  ): void

  [USER_STORE.ACTIONS.UPDATE_USER_PREFERENCES](
    context: ActionContext<IUserState, IRootState>,
    payload: IUserPreferencesPayload
  ): void

  [USER_STORE.ACTIONS.UPDATE_USER_PICTURE](
    context: ActionContext<IUserState, IRootState>,
    payload: IUserPicturePayload
  ): void

  [USER_STORE.ACTIONS.SEND_PASSWORD_RESET_REQUEST](
    context: ActionContext<IUserState, IRootState>,
    payload: IUserPasswordPayload
  ): void

  [USER_STORE.ACTIONS.RESET_USER_PASSWORD](
    context: ActionContext<IUserState, IRootState>,
    payload: IUserPasswordResetPayload
  ): void

  [USER_STORE.ACTIONS.DELETE_ACCOUNT](
    context: ActionContext<IUserState, IRootState>,
    payload: IUserDeletionPayload
  ): void

  [USER_STORE.ACTIONS.DELETE_PICTURE](
    context: ActionContext<IUserState, IRootState>
  ): void
}

export interface IUserGetters {
  [USER_STORE.GETTERS.AUTH_TOKEN](state: IUserState): string | null

  [USER_STORE.GETTERS.AUTH_USER_PROFILE](state: IUserState): IUserProfile

  [USER_STORE.GETTERS.IS_ADMIN](state: IUserState): boolean

  [USER_STORE.GETTERS.IS_AUTHENTICATED](state: IUserState): boolean

  [USER_STORE.GETTERS.USER_LOADING](state: IUserState): boolean
}

export type TUserMutations<S = IUserState> = {
  [USER_STORE.MUTATIONS.CLEAR_AUTH_USER_TOKEN](state: S): void
  [USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN](state: S, authToken: string): void
  [USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE](
    state: S,
    authUserProfile: IUserProfile
  ): void
  [USER_STORE.MUTATIONS.UPDATE_USER_LOADING](state: S, loading: boolean): void
}

export type TUserStoreModule<S = IUserState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IUserActions>(
    key: K,
    payload?: Parameters<IUserActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IUserActions[K]>
} & {
  getters: {
    [K in keyof IUserGetters]: ReturnType<IUserGetters[K]>
  }
} & {
  commit<
    K extends keyof TUserMutations,
    P extends Parameters<TUserMutations[K]>[1]
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TUserMutations[K]>
}
