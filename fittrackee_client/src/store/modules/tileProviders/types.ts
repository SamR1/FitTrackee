import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { TILE_PROVIDERS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type {
  ITileProvider,
  ITileProviderForAdmin,
  ITileProviderPayload,
} from '@/types/tileProviders'

export interface ITileProvidersState {
  tileProviders: ITileProvider[] | ITileProviderForAdmin[]
}

export interface ITileProvidersActions {
  [TILE_PROVIDERS_STORE.ACTIONS.GET_TILE_PROVIDERS](
    context: ActionContext<ITileProvidersState, IRootState>
  ): void
  [TILE_PROVIDERS_STORE.ACTIONS.UPDATE_TILE_PROVIDER](
    context: ActionContext<ITileProvidersState, IRootState>,
    payload: ITileProviderPayload
  ): void
}

export interface ITileProvidersGetters {
  [TILE_PROVIDERS_STORE.GETTERS.TILE_PROVIDERS](
    state: ITileProvidersState
  ): ITileProvider[] | ITileProviderForAdmin[]
}

export type TTileProvidersMutations<S = ITileProvidersState> = {
  [TILE_PROVIDERS_STORE.MUTATIONS.SET_TILE_PROVIDER](
    state: S,
    tileProviders: ITileProviderForAdmin[]
  ): void
}

export type TTileProvidersStoreModule<S = ITileProvidersState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof ITileProvidersActions>(
    key: K,
    payload?: Parameters<ITileProvidersActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<ITileProvidersActions[K]>
} & {
  getters: {
    [K in keyof ITileProvidersGetters]: ReturnType<ITileProvidersGetters[K]>
  }
} & {
  commit<
    K extends keyof TTileProvidersMutations,
    P extends Parameters<TTileProvidersMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TTileProvidersMutations[K]>
}
