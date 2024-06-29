import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { STATS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type {
  IUserSportStatisticsPayload,
  IUserStatisticsPayload,
  TSportStatisticsFromApi,
  TStatisticsFromApi,
} from '@/types/statistics'

export interface IStatisticsState {
  statistics: TStatisticsFromApi
  sportStatistics: TSportStatisticsFromApi
  totalWorkouts: number
  loading: boolean
}

export interface IStatisticsActions {
  [STATS_STORE.ACTIONS.GET_USER_STATS](
    context: ActionContext<IStatisticsState, IRootState>,
    payload: IUserStatisticsPayload
  ): void
  [STATS_STORE.ACTIONS.GET_USER_SPORT_STATS](
    context: ActionContext<IStatisticsState, IRootState>,
    payload: IUserSportStatisticsPayload
  ): void
}

export interface IStatisticsGetters {
  [STATS_STORE.GETTERS.USER_SPORT_STATS](
    state: IStatisticsState
  ): TSportStatisticsFromApi
  [STATS_STORE.GETTERS.USER_STATS](state: IStatisticsState): TStatisticsFromApi
  [STATS_STORE.GETTERS.STATS_LOADING](state: IStatisticsState): boolean
  [STATS_STORE.GETTERS.TOTAL_WORKOUTS](state: IStatisticsState): number
}

export type TStatisticsMutations<S = IStatisticsState> = {
  [STATS_STORE.MUTATIONS.UPDATE_USER_SPORT_STATS](
    state: S,
    sportStatistics: TSportStatisticsFromApi
  ): void
  [STATS_STORE.MUTATIONS.UPDATE_USER_STATS](
    state: S,
    statistics: TStatisticsFromApi
  ): void
  [STATS_STORE.MUTATIONS.EMPTY_USER_SPORT_STATS](state: S): void
  [STATS_STORE.MUTATIONS.EMPTY_USER_STATS](state: S): void
  [STATS_STORE.MUTATIONS.UPDATE_STATS_LOADING](state: S, loading: boolean): void
  [STATS_STORE.MUTATIONS.UPDATE_TOTAL_WORKOUTS](
    state: S,
    totalWorkouts: number
  ): void
}

export type TStatisticsStoreModule<S = IStatisticsState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IStatisticsActions>(
    key: K,
    payload?: Parameters<IStatisticsActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IStatisticsActions[K]>
} & {
  getters: {
    [K in keyof IStatisticsGetters]: ReturnType<IStatisticsGetters[K]>
  }
} & {
  commit<
    K extends keyof TStatisticsMutations,
    P extends Parameters<TStatisticsMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TStatisticsMutations[K]>
}
