import type { Module } from 'vuex'

import { actions } from '@/store/modules/oauth2/actions'
import { getters } from '@/store/modules/oauth2/getters'
import { mutations } from '@/store/modules/oauth2/mutations'
import { oAuth2State } from '@/store/modules/oauth2/state'
import type { IOAuth2State } from '@/store/modules/oauth2/types'
import type { IRootState } from '@/store/modules/root/types'

const oauth2: Module<IOAuth2State, IRootState> = {
  state: oAuth2State,
  actions,
  getters,
  mutations,
}

export default oauth2
