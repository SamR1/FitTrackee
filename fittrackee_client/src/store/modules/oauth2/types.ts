import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { OAUTH2_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IPagination } from '@/types/api'
import { IOAuth2Client, IOauth2ClientsPayload } from '@/types/oauth'

export interface IOAuth2State {
  clients: IOAuth2Client[]
  pagination: IPagination
}

export interface IOAuth2Actions {
  [OAUTH2_STORE.ACTIONS.GET_CLIENTS](
    context: ActionContext<IOAuth2State, IRootState>,
    payload: IOauth2ClientsPayload
  ): void
}

export interface IOAuth2Getters {
  [OAUTH2_STORE.GETTERS.CLIENTS](state: IOAuth2State): IOAuth2Client[]
  [OAUTH2_STORE.GETTERS.CLIENTS_PAGINATION](state: IOAuth2State): IPagination
}

export type TOAuth2Mutations<S = IOAuth2State> = {
  [OAUTH2_STORE.MUTATIONS.SET_CLIENTS](state: S, clients: IOAuth2Client[]): void
  [OAUTH2_STORE.MUTATIONS.SET_CLIENTS_PAGINATION](
    state: S,
    pagination: IPagination
  ): void
}

export type TOAuth2StoreModule<S = IOAuth2State> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IOAuth2Actions>(
    key: K,
    payload?: Parameters<IOAuth2Actions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IOAuth2Actions[K]>
} & {
  getters: {
    [K in keyof IOAuth2Getters]: ReturnType<IOAuth2Getters[K]>
  }
} & {
  commit<
    K extends keyof TOAuth2Mutations,
    P extends Parameters<TOAuth2Mutations[K]>[1]
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TOAuth2Mutations[K]>
}
