import type { IReportsState } from '@/store/modules/reports/types'
import type { IPagination } from '@/types/api'
import type { IReportForModerator } from '@/types/reports'

export const reportsState: IReportsState = {
  unresolved: false,
  report: <IReportForModerator>{},
  reports: [],
  pagination: <IPagination>{},
  reportStatus: null,
  reportLoading: false,
  reportUpdateLoading: false,
}
