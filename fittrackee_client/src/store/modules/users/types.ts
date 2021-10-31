import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { USERS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IPagination, TPaginationPayload } from '@/types/api'
import { IAdminUserPayload, IUserProfile } from '@/types/user'

export interface IUsersState {
  users: IUserProfile[]
  loading: boolean
  pagination: IPagination
}

export interface IUsersActions {
  [USERS_STORE.ACTIONS.GET_USERS](
    context: ActionContext<IUsersState, IRootState>,
    payload: TPaginationPayload
  ): void
  [USERS_STORE.ACTIONS.UPDATE_USER](
    context: ActionContext<IUsersState, IRootState>,
    payload: IAdminUserPayload
  ): void
}

export interface IUsersGetters {
  [USERS_STORE.GETTERS.USERS](state: IUsersState): IUserProfile[]
  [USERS_STORE.GETTERS.USERS_LOADING](state: IUsersState): boolean
  [USERS_STORE.GETTERS.USERS_PAGINATION](state: IUsersState): IPagination
}

export type TUsersMutations<S = IUsersState> = {
  [USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS](
    state: S,
    updatedUser: IUserProfile
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS](state: S, users: IUserProfile[]): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING](state: S, loading: boolean): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS_PAGINATION](
    state: S,
    pagination: IPagination
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
