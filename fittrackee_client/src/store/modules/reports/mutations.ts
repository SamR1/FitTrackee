import type { MutationTree } from 'vuex'

import { REPORTS_STORE } from '@/store/constants'
import type {
  IReportsState,
  TReportsMutations,
} from '@/store/modules/reports/types'
import type { IPagination } from '@/types/api'
import type { IReportForModerator } from '@/types/reports'

export const mutations: MutationTree<IReportsState> & TReportsMutations = {
  [REPORTS_STORE.MUTATIONS.EMPTY_REPORT](state: IReportsState) {
    state.report = <IReportForModerator>{}
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORT](
    state: IReportsState,
    report: IReportForModerator
  ) {
    state.report = report
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORT_LOADING](
    state: IReportsState,
    reportLoading: boolean
  ) {
    state.reportLoading = reportLoading
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS](
    state: IReportsState,
    reportStatus: string | null
  ) {
    state.reportStatus = reportStatus
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORT_UPDATE_LOADING](
    state: IReportsState,
    reportUpdateLoading: boolean
  ) {
    state.reportUpdateLoading = reportUpdateLoading
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORTS](
    state: IReportsState,
    reports: IReportForModerator[]
  ) {
    state.reports = reports
  },
  [REPORTS_STORE.MUTATIONS.SET_REPORTS_PAGINATION](
    state: IReportsState,
    pagination: IPagination
  ) {
    state.pagination = pagination
  },
  [REPORTS_STORE.MUTATIONS.SET_UNRESOLVED_REPORTS_STATUS](
    state: IReportsState,
    unresolved: boolean
  ) {
    state.unresolved = unresolved
  },
}
