import { MutationTree } from 'vuex'

import { OAUTH2_STORE } from '@/store/constants'
import { IOAuth2State, TOAuth2Mutations } from '@/store/modules/oauth2/types'
import { IPagination } from '@/types/api'
import { IOAuth2Client } from '@/types/oauth'

export const mutations: MutationTree<IOAuth2State> & TOAuth2Mutations = {
  [OAUTH2_STORE.MUTATIONS.SET_CLIENT](
    state: IOAuth2State,
    client: IOAuth2Client
  ) {
    state.client = client
  },
  [OAUTH2_STORE.MUTATIONS.EMPTY_CLIENT](state: IOAuth2State) {
    state.client = <IOAuth2Client>{}
  },
  [OAUTH2_STORE.MUTATIONS.SET_CLIENTS](
    state: IOAuth2State,
    clients: IOAuth2Client[]
  ) {
    state.clients = clients
  },
  [OAUTH2_STORE.MUTATIONS.SET_CLIENTS_PAGINATION](
    state: IOAuth2State,
    pagination: IPagination
  ) {
    state.pagination = pagination
  },
}
