import { GetterTree } from 'vuex'

import { REPORTS_STORE } from '@/store/constants'
import { IReportsGetters, IReportsState } from '@/store/modules/reports/types'
import { IRootState } from '@/store/modules/root/types'

export const getters: GetterTree<IReportsState, IRootState> & IReportsGetters =
  {
    [REPORTS_STORE.GETTERS.REPORTS]: (state: IReportsState) => state.reports,
    [REPORTS_STORE.GETTERS.REPORT_STATUS]: (state: IReportsState) =>
      state.reportStatus,
  }
