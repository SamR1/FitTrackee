import { Store as VuexStore, CommitOptions, DispatchOptions } from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import {
  IRootActions,
  IRootGetters,
  IRootState,
} from '@/store/modules/root/interfaces'

export type TRootMutations<S = IRootState> = {
  [ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES](state: S): void
  [ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES](
    state: S,
    errorMessages: string
  ): void
  [ROOT_STORE.MUTATIONS.UPDATE_LANG](state: S, language: string): void
}

export type TRootStoreModule<S = IRootState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IRootActions>(
    key: K,
    payload?: Parameters<IRootActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IRootActions[K]>
} & {
  getters: {
    [K in keyof IRootGetters]: ReturnType<IRootGetters[K]>
  }
} & {
  commit<
    K extends keyof TRootMutations,
    P extends Parameters<TRootMutations[K]>[1]
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TRootMutations[K]>
}
