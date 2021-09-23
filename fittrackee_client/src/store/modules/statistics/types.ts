import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { STATS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IUserStatisticsPayload, TStatisticsFromApi } from '@/types/statistics'

export interface IStatisticsState {
  statistics: TStatisticsFromApi
}

export interface IStatisticsActions {
  [STATS_STORE.ACTIONS.GET_USER_STATS](
    context: ActionContext<IStatisticsState, IRootState>,
    payload: IUserStatisticsPayload
  ): void
}

export interface IStatisticsGetters {
  [STATS_STORE.GETTERS.USER_STATS](state: IStatisticsState): TStatisticsFromApi
}

export type TStatisticsMutations<S = IStatisticsState> = {
  [STATS_STORE.MUTATIONS.UPDATE_USER_STATS](
    state: S,
    statistics: TStatisticsFromApi
  ): void
  [STATS_STORE.MUTATIONS.EMPTY_USER_STATS](state: S): void
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
