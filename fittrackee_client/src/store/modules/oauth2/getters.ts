import type { GetterTree } from 'vuex'

import { OAUTH2_STORE } from '@/store/constants'
import type { IOAuth2Getters, IOAuth2State } from '@/store/modules/oauth2/types'
import type { IRootState } from '@/store/modules/root/types'

export const getters: GetterTree<IOAuth2State, IRootState> & IOAuth2Getters = {
  [OAUTH2_STORE.GETTERS.CLIENT]: (state: IOAuth2State) => state.client,
  [OAUTH2_STORE.GETTERS.CLIENTS]: (state: IOAuth2State) => state.clients,
  [OAUTH2_STORE.GETTERS.CLIENTS_PAGINATION]: (state: IOAuth2State) =>
    state.pagination,
  [OAUTH2_STORE.GETTERS.REVOCATION_SUCCESSFUL]: (state: IOAuth2State) =>
    state.revocationSuccessful,
}
