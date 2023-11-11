import type { Module } from 'vuex'

import type { IRootState } from '@/store/modules/root/types'
import { actions } from '@/store/modules/sports/actions'
import { getters } from '@/store/modules/sports/getters'
import { mutations } from '@/store/modules/sports/mutations'
import { sportsState } from '@/store/modules/sports/state'
import type { ISportsState } from '@/store/modules/sports/types'

const sports: Module<ISportsState, IRootState> = {
  state: sportsState,
  actions,
  getters,
  mutations,
}

export default sports
