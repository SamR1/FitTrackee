import type { GetterTree } from 'vuex'

import { TILE_PROVIDERS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type {
  ITileProvidersGetters,
  ITileProvidersState,
} from '@/store/modules/tileProviders/types'

export const getters: GetterTree<ITileProvidersState, IRootState> &
  ITileProvidersGetters = {
  [TILE_PROVIDERS_STORE.GETTERS.TILE_PROVIDERS]: (state: ITileProvidersState) =>
    state.tileProviders,
}
