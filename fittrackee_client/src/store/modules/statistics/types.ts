import { Store as VuexStore, CommitOptions, DispatchOptions } from 'vuex'

import { STATS_STORE } from '@/store/constants'
import {
  IStatisticsState,
  IStatisticsActions,
  IStatisticsGetters,
} from '@/store/modules/statistics/interfaces'
import { TStatistics } from '@/types/statistics'

export type TStatisticsMutations<S = IStatisticsState> = {
  [STATS_STORE.MUTATIONS.UPDATE_USER_STATS](
    state: S,
    statistics: TStatistics
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
    P extends Parameters<TStatisticsMutations[K]>[1]
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TStatisticsMutations[K]>
}
