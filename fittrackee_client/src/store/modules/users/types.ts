import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { USERS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IPagination } from '@/types/api'
import {
  IAdminUserPayload,
  IUserDeletionPayload,
  IUserProfile,
  IUserRelationshipActionPayload,
  IUserRelationshipsPayload,
  TUsersPayload,
} from '@/types/user'

export interface IUsersState {
  user: IUserProfile
  user_relationships: IUserProfile[]
  users: IUserProfile[]
  loading: boolean
  isSuccess: boolean
  pagination: IPagination
  currentReporting: boolean
}

export interface IUsersActions {
  [USERS_STORE.ACTIONS.EMPTY_USER](
    context: ActionContext<IUsersState, IRootState>
  ): void
  [USERS_STORE.ACTIONS.EMPTY_USERS](
    context: ActionContext<IUsersState, IRootState>
  ): void
  [USERS_STORE.ACTIONS.EMPTY_RELATIONSHIPS](
    context: ActionContext<IUsersState, IRootState>
  ): void
  [USERS_STORE.ACTIONS.GET_USER](
    context: ActionContext<IUsersState, IRootState>,
    username: string
  ): void
  [USERS_STORE.ACTIONS.GET_USERS](
    context: ActionContext<IUsersState, IRootState>,
    payload: TUsersPayload
  ): void
  [USERS_STORE.ACTIONS.GET_USERS_FOR_ADMIN](
    context: ActionContext<IUsersState, IRootState>,
    payload: TUsersPayload
  ): void
  [USERS_STORE.ACTIONS.UPDATE_USER](
    context: ActionContext<IUsersState, IRootState>,
    payload: IAdminUserPayload
  ): void
  [USERS_STORE.ACTIONS.UPDATE_RELATIONSHIP](
    context: ActionContext<IUsersState, IRootState>,
    payload: IUserRelationshipActionPayload
  ): void
  [USERS_STORE.ACTIONS.GET_RELATIONSHIPS](
    context: ActionContext<IUsersState, IRootState>,
    payload: IUserRelationshipsPayload
  ): void
  [USERS_STORE.ACTIONS.DELETE_USER_ACCOUNT](
    context: ActionContext<IUsersState, IRootState>,
    payload: IUserDeletionPayload
  ): void
}

export interface IUsersGetters {
  [USERS_STORE.GETTERS.USER](state: IUsersState): IUserProfile
  [USERS_STORE.GETTERS.USER_CURRENT_REPORTING](state: IUsersState): boolean
  [USERS_STORE.GETTERS.USER_RELATIONSHIPS](state: IUsersState): IUserProfile[]
  [USERS_STORE.GETTERS.USERS](state: IUsersState): IUserProfile[]
  [USERS_STORE.GETTERS.USERS_IS_SUCCESS](state: IUsersState): boolean
  [USERS_STORE.GETTERS.USERS_LOADING](state: IUsersState): boolean
  [USERS_STORE.GETTERS.USERS_PAGINATION](state: IUsersState): IPagination
}

export type TUsersMutations<S = IUsersState> = {
  [USERS_STORE.MUTATIONS.UPDATE_USER](state: S, user: IUserProfile): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS](
    state: S,
    updatedUser: IUserProfile
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_IN_RELATIONSHIPS](
    state: S,
    updatedUser: IUserProfile
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_RELATIONSHIPS](
    state: S,
    relationship: IUserProfile[]
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS](state: S, users: IUserProfile[]): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING](state: S, loading: boolean): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS_PAGINATION](
    state: S,
    pagination: IPagination
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS](state: S, isSuccess: boolean): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_CURRENT_REPORTING](
    state: S,
    currentReporting: boolean
  ): void
}

export type TUsersStoreModule<S = IUsersState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IUsersActions>(
    key: K,
    payload?: Parameters<IUsersActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IUsersActions[K]>
} & {
  getters: {
    [K in keyof IUsersGetters]: ReturnType<IUsersGetters[K]>
  }
} & {
  commit<
    K extends keyof TUsersMutations,
    P extends Parameters<TUsersMutations[K]>[1]
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TUsersMutations[K]>
}
