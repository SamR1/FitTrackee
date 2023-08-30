import { MutationTree } from 'vuex'

import { REPORTS_STORE } from '@/store/constants'
import { IReportsState, TReportsMutations } from '@/store/modules/reports/types'
import { IReportForAdmin } from '@/types/reports'

export const mutations: MutationTree<IReportsState> & TReportsMutations = {
  [REPORTS_STORE.MUTATIONS.SET_REPORTS](
    state: IReportsState,
    reports: IReportForAdmin[]
  ) {
    state.reports = reports
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS](
    state: IReportsState,
    reportStatus: string | null
  ) {
    state.reportStatus = reportStatus
  },
}
