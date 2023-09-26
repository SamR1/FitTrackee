import { MutationTree } from 'vuex'

import { REPORTS_STORE } from '@/store/constants'
import { IReportsState, TReportsMutations } from '@/store/modules/reports/types'
import { IPagination } from '@/types/api'
import { IReportForAdmin } from '@/types/reports'

export const mutations: MutationTree<IReportsState> & TReportsMutations = {
  [REPORTS_STORE.MUTATIONS.EMPTY_REPORT](state: IReportsState) {
    state.report = <IReportForAdmin>{}
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORT](
    state: IReportsState,
    report: IReportForAdmin
  ) {
    state.report = report
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORTS](
    state: IReportsState,
    reports: IReportForAdmin[]
  ) {
    state.reports = reports
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORTS_PAGINATION](
    state: IReportsState,
    pagination: IPagination
  ) {
    state.pagination = pagination
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS](
    state: IReportsState,
    reportStatus: string | null
  ) {
    state.reportStatus = reportStatus
  },
}
