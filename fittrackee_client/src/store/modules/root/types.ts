import type { Locale } from 'date-fns'
import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import type {
  TAppConfig,
  IApplication,
  IAppStatistics,
  TAppConfigForm,
} from '@/types/application'

export interface IRootState {
  root: boolean
  language: string
  locale: Locale
  errorMessages: string | string[] | null
  application: IApplication
  appLoading: boolean
}

export interface IRootActions {
  [ROOT_STORE.ACTIONS.GET_APPLICATION_CONFIG](
    context: ActionContext<IRootState, IRootState>
  ): void
  [ROOT_STORE.ACTIONS.GET_APPLICATION_STATS](
    context: ActionContext<IRootState, IRootState>
  ): void
  [ROOT_STORE.ACTIONS.GET_APPLICATION_PRIVACY_POLICY](
    context: ActionContext<IRootState, IRootState>
  ): void
  [ROOT_STORE.ACTIONS.UPDATE_APPLICATION_CONFIG](
    context: ActionContext<IRootState, IRootState>,
    payload: TAppConfigForm
  ): void
  [ROOT_STORE.ACTIONS.UPDATE_APPLICATION_LANGUAGE](
    context: ActionContext<IRootState, IRootState>,
    langauge: string
  ): void
}

export interface IRootGetters {
  [ROOT_STORE.GETTERS.APP_CONFIG](state: IRootState): TAppConfig

  [ROOT_STORE.GETTERS.APP_LOADING](state: IRootState): boolean

  [ROOT_STORE.GETTERS.APP_STATS](state: IRootState): IAppStatistics

  [ROOT_STORE.GETTERS.ERROR_MESSAGES](
    state: IRootState
  ): string | string[] | null

  [ROOT_STORE.GETTERS.LANGUAGE](state: IRootState): string

  [ROOT_STORE.GETTERS.LOCALE](state: IRootState): Locale
}

export type TRootMutations<S = IRootState> = {
  [ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES](state: S): void
  [ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES](
    state: S,
    errorMessages: string | string[]
  ): void
  [ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_CONFIG](
    state: S,
    config: TAppConfig
  ): void
  [ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_LOADING](
    state: S,
    loading: boolean
  ): void
  [ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_PRIVACY_POLICY](
    state: S,
    config: TAppConfig
  ): void
  [ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_STATS](
    state: S,
    statistics: IAppStatistics
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
    P extends Parameters<TRootMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TRootMutations[K]>
}
