import { GetterTree } from 'vuex'

import { SPORTS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { ISportsGetters, ISportsState } from '@/store/modules/sports/types'

export const getters: GetterTree<ISportsState, IRootState> & ISportsGetters = {
  [SPORTS_STORE.GETTERS.SPORTS]: (state: ISportsState) => state.sports,
}
