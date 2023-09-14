import { IReportsState } from '@/store/modules/reports/types'
import { IPagination } from '@/types/api'
import { IReportForAdmin } from '@/types/reports'

export const reportsState: IReportsState = {
  report: <IReportForAdmin>{},
  reports: [],
  pagination: <IPagination>{},
  reportStatus: null,
}
