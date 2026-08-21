import type { Module } from 'vuex'

import type { IRootState } from '@/store/modules/root/types'
import { actions } from '@/store/modules/tileProviders/actions'
import { getters } from '@/store/modules/tileProviders/getters'
import { mutations } from '@/store/modules/tileProviders/mutations'
import { tileProvidersState } from '@/store/modules/tileProviders/state'
import type { ITileProvidersState } from '@/store/modules/tileProviders/types'

const tileProviders: Module<ITileProvidersState, IRootState> = {
  state: tileProvidersState,
  actions,
  getters,
  mutations,
}

export default tileProviders
