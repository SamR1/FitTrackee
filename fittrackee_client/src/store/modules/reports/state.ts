import type { IReportsState } from '@/store/modules/reports/types'
import type { IPagination } from '@/types/api'
import type { IReportForAdmin } from '@/types/reports'

export const reportsState: IReportsState = {
  report: <IReportForAdmin>{},
  reports: [],
  pagination: <IPagination>{},
  reportStatus: null,
  reportLoading: false,
  reportUpdateLoading: false,
}
