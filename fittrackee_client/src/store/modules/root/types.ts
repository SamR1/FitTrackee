import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import { IAppConfig, IApplication } from '@/types/application'

export interface IRootState {
  root: boolean
  language: string
  errorMessages: string | string[] | null
  application: IApplication
  appLoading: boolean
}

export interface IRootActions {
  [ROOT_STORE.ACTIONS.GET_APPLICATION_CONFIG](
    context: ActionContext<IRootState, IRootState>
  ): void
}

export interface IRootGetters {
  [ROOT_STORE.GETTERS.APP_CONFIG](state: IRootState): IAppConfig

  [ROOT_STORE.GETTERS.APP_LOADING](state: IRootState): boolean

  [ROOT_STORE.GETTERS.ERROR_MESSAGES](
    state: IRootState
  ): string | string[] | null

  [ROOT_STORE.GETTERS.LANGUAGE](state: IRootState): string
}

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
