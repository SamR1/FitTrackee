import { MutationTree } from 'vuex'

import { SPORTS_STORE } from '@/store/constants'
import { ISportsState, TSportsMutations } from '@/store/modules/sports/types'
import { ISport } from '@/types/sports'

export const mutations: MutationTree<ISportsState> & TSportsMutations = {
  [SPORTS_STORE.MUTATIONS.SET_SPORTS](state: ISportsState, sports: ISport[]) {
    state.sports = sports
  },
}
