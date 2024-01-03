import type { GetterTree } from 'vuex'

import { SPORTS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { ISportsGetters, ISportsState } from '@/store/modules/sports/types'

export const getters: GetterTree<ISportsState, IRootState> & ISportsGetters = {
  [SPORTS_STORE.GETTERS.SPORTS]: (state: ISportsState) => state.sports,
}
