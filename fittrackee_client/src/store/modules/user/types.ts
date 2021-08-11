import { Store as VuexStore, CommitOptions, DispatchOptions } from 'vuex'

import { USER_STORE } from '@/store/constants'
import {
  IUserActions,
  IUserGetters,
  IUserState,
} from '@/store/modules/user/interfaces'

export type TUserMutations<S = IUserState> = {
  [USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN](state: S, authToken: string): void
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
