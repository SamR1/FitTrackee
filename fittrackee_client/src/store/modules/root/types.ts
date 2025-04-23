import type { Locale } from 'date-fns'
import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import type { IPagination } from '@/types/api.ts'
import type {
  TAppConfig,
  IApplication,
  IAppStatistics,
  TAppConfigForm,
  IDisplayOptions,
  IQueuedTask,
  IQueuedTasksPayload,
  TQueuedTasksCounts,
} from '@/types/application'
import type { IEquipmentError } from '@/types/equipments'
import type { TLanguage } from '@/types/locales'
import type { IAuthUserProfile } from '@/types/user'

export interface IRootState {
  root: boolean
  language: TLanguage
  locale: Locale
  errorMessages: string | string[] | IEquipmentError | null
  application: IApplication
  appLoading: boolean
  darkMode: boolean | null
  queuedTasks: {
    counts: TQueuedTasksCounts
    tasks: IQueuedTask[]
    pagination: IPagination
  }
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
  [ROOT_STORE.ACTIONS.GET_QUEUED_TASKS_LIST](
    context: ActionContext<IRootState, IRootState>,
    payload: IQueuedTasksPayload
  ): void
  [ROOT_STORE.ACTIONS.GET_QUEUED_TASKS_COUNT](
    context: ActionContext<IRootState, IRootState>
  ): void
  [ROOT_STORE.ACTIONS.UPDATE_APPLICATION_CONFIG](
    context: ActionContext<IRootState, IRootState>,
    payload: TAppConfigForm
  ): void
  [ROOT_STORE.ACTIONS.UPDATE_APPLICATION_LANGUAGE](
    context: ActionContext<IRootState, IRootState>,
    language: TLanguage
  ): void
}

export interface IRootGetters {
  [ROOT_STORE.GETTERS.APP_CONFIG](state: IRootState): TAppConfig

  [ROOT_STORE.GETTERS.APP_LOADING](state: IRootState): boolean

  [ROOT_STORE.GETTERS.APP_STATS](state: IRootState): IAppStatistics

  [ROOT_STORE.GETTERS.DARK_MODE](state: IRootState): boolean | null

  [ROOT_STORE.GETTERS.ERROR_MESSAGES](
    state: IRootState
  ): string | string[] | IEquipmentError | null

  [ROOT_STORE.GETTERS.LANGUAGE](state: IRootState): TLanguage

  [ROOT_STORE.GETTERS.LOCALE](state: IRootState): Locale
  [ROOT_STORE.GETTERS.DISPLAY_OPTIONS](state: IRootState): IDisplayOptions
  [ROOT_STORE.GETTERS.QUEUED_TASKS](state: IRootState): IQueuedTask[]
  [ROOT_STORE.GETTERS.QUEUED_TASKS_COUNTS](
    state: IRootState
  ): TQueuedTasksCounts
  [ROOT_STORE.GETTERS.QUEUED_TASKS_PAGINATION](state: IRootState): IPagination
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
  [ROOT_STORE.MUTATIONS.UPDATE_LANG](state: S, language: TLanguage): void
  [ROOT_STORE.MUTATIONS.UPDATE_DARK_MODE](
    state: S,
    darkMode: boolean | null
  ): void
  [ROOT_STORE.MUTATIONS.UPDATE_DISPLAY_OPTIONS](
    state: S,
    authUser: IAuthUserProfile
  ): void
  [ROOT_STORE.MUTATIONS.UPDATE_QUEUED_TASKS](
    state: S,
    tasks: IQueuedTask[]
  ): void
  [ROOT_STORE.MUTATIONS.UPDATE_QUEUED_TASKS_COUNTS](
    state: S,
    counts: TQueuedTasksCounts
  ): void
  [ROOT_STORE.MUTATIONS.UPDATE_QUEUED_TASKS_PAGINATION](
    state: S,
    pagination: IPagination
  ): void
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
