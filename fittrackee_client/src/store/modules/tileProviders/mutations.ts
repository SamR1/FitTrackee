import type { MutationTree } from 'vuex'

import { TILE_PROVIDERS_STORE } from '@/store/constants'
import type {
  ITileProvidersState,
  TTileProvidersMutations,
} from '@/store/modules/tileProviders/types'
import type {
  ITileProviderForAdmin,
  ITileProvider,
} from '@/types/tileProviders'

export const mutations: MutationTree<ITileProvidersState> &
  TTileProvidersMutations = {
  [TILE_PROVIDERS_STORE.MUTATIONS.SET_TILE_PROVIDER](
    state: ITileProvidersState,
    tileProviders: ITileProvider[] | ITileProviderForAdmin[]
  ) {
    state.tileProviders = tileProviders
  },
}
