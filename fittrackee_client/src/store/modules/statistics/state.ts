import type { IStatisticsState } from '@/store/modules/statistics/types'
import type { TStatisticsFromApi } from '@/types/statistics'

export const statisticsState: IStatisticsState = {
  statistics: <TStatisticsFromApi>{},
}
