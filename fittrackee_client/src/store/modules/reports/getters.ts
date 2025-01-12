import type { GetterTree } from 'vuex'

import { REPORTS_STORE } from '@/store/constants'
import type {
  IReportsGetters,
  IReportsState,
} from '@/store/modules/reports/types'
import type { IRootState } from '@/store/modules/root/types'

export const getters: GetterTree<IReportsState, IRootState> & IReportsGetters =
  {
    [REPORTS_STORE.GETTERS.UNRESOLVED_REPORTS_STATUS]: (state: IReportsState) =>
      state.unresolved,
    [REPORTS_STORE.GETTERS.REPORT]: (state: IReportsState) => state.report,
    [REPORTS_STORE.GETTERS.REPORT_LOADING]: (state: IReportsState) =>
      state.reportLoading,
    [REPORTS_STORE.GETTERS.REPORT_STATUS]: (state: IReportsState) =>
      state.reportStatus,
    [REPORTS_STORE.GETTERS.REPORT_UPDATE_LOADING]: (state: IReportsState) =>
      state.reportUpdateLoading,
    [REPORTS_STORE.GETTERS.REPORTS]: (state: IReportsState) => state.reports,
    [REPORTS_STORE.GETTERS.REPORTS_PAGINATION]: (state: IReportsState) =>
      state.pagination,
  }
