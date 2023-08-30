import { IReportsState } from '@/store/modules/reports/types'
import { IPagination } from '@/types/api'

export const reportsState: IReportsState = {
  reports: [],
  pagination: <IPagination>{},
  reportStatus: null,
}
