import { Store as VuexStore, CommitOptions } from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import { IRootGetters, IRootState } from '@/store/modules/root/interfaces'

export type TRootMutations<S = IRootState> = {
  [ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGE](state: S): void
  [ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGE](state: S, errorMessage: string): void
  [ROOT_STORE.MUTATIONS.UPDATE_LANG](state: S, language: string): void
}

export type TRootStoreModule<S = IRootState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
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
