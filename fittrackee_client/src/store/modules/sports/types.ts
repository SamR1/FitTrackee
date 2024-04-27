import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { SPORTS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { ISport, ISportPayload } from '@/types/sports'

export interface ISportsState {
  sports: ISport[]
}

export interface ISportsActions {
  [SPORTS_STORE.ACTIONS.GET_SPORTS](
    context: ActionContext<ISportsState, IRootState>,
    checkWorkouts: boolean
  ): void
  [SPORTS_STORE.ACTIONS.UPDATE_SPORTS](
    context: ActionContext<ISportsState, IRootState>,
    payload: ISportPayload
  ): void
}

export interface ISportsGetters {
  [SPORTS_STORE.GETTERS.SPORTS](state: ISportsState): ISport[]
}

export type TSportsMutations<S = ISportsState> = {
  [SPORTS_STORE.MUTATIONS.SET_SPORTS](state: S, sports: ISport[]): void
}

export type TSportsStoreModule<S = ISportsState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof ISportsActions>(
    key: K,
    payload?: Parameters<ISportsActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<ISportsActions[K]>
} & {
  getters: {
    [K in keyof ISportsGetters]: ReturnType<ISportsGetters[K]>
  }
} & {
  commit<
    K extends keyof TSportsMutations,
    P extends Parameters<TSportsMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TSportsMutations[K]>
}
