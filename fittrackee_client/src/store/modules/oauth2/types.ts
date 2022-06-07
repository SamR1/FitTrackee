import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { OAUTH2_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IPagination } from '@/types/api'
import {
  IOAuth2Client,
  IOAuth2ClientAuthorizePayload,
  IOAuth2ClientPayload,
  IOauth2ClientsPayload,
} from '@/types/oauth'

export interface IOAuth2State {
  client: IOAuth2Client
  clients: IOAuth2Client[]
  pagination: IPagination
}

export interface IOAuth2Actions {
  [OAUTH2_STORE.ACTIONS.AUTHORIZE_CLIENT](
    context: ActionContext<IOAuth2State, IRootState>,
    payload: IOAuth2ClientAuthorizePayload
  ): void
  [OAUTH2_STORE.ACTIONS.CREATE_CLIENT](
    context: ActionContext<IOAuth2State, IRootState>,
    payload: IOAuth2ClientPayload
  ): void
  [OAUTH2_STORE.ACTIONS.DELETE_CLIENT](
    context: ActionContext<IOAuth2State, IRootState>,
    id: number
  ): void
  [OAUTH2_STORE.ACTIONS.GET_CLIENT_BY_CLIENT_ID](
    context: ActionContext<IOAuth2State, IRootState>,
    client_id: string
  ): void
  [OAUTH2_STORE.ACTIONS.GET_CLIENT_BY_ID](
    context: ActionContext<IOAuth2State, IRootState>,
    id: number
  ): void
  [OAUTH2_STORE.ACTIONS.GET_CLIENTS](
    context: ActionContext<IOAuth2State, IRootState>,
    payload: IOauth2ClientsPayload
  ): void
}

export interface IOAuth2Getters {
  [OAUTH2_STORE.GETTERS.CLIENT](state: IOAuth2State): IOAuth2Client
  [OAUTH2_STORE.GETTERS.CLIENTS](state: IOAuth2State): IOAuth2Client[]
  [OAUTH2_STORE.GETTERS.CLIENTS_PAGINATION](state: IOAuth2State): IPagination
}

export type TOAuth2Mutations<S = IOAuth2State> = {
  [OAUTH2_STORE.MUTATIONS.EMPTY_CLIENT](state: S): void
  [OAUTH2_STORE.MUTATIONS.SET_CLIENT](state: S, client: IOAuth2Client): void
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
