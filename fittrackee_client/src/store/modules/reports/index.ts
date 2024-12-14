import type { Module } from 'vuex'

import { actions } from '@/store/modules/reports/actions'
import { getters } from '@/store/modules/reports/getters'
import { mutations } from '@/store/modules/reports/mutations'
import { reportsState } from '@/store/modules/reports/state'
import type { IReportsState } from '@/store/modules/reports/types'
import type { IRootState } from '@/store/modules/root/types'

const reports: Module<IReportsState, IRootState> = {
  state: reportsState,
  actions,
  getters,
  mutations,
}

export default reports
