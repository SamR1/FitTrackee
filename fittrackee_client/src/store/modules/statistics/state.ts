import { IStatisticsState } from '@/store/modules/statistics/types'
import { TStatisticsFromApi } from '@/types/statistics'

export const statisticsState: IStatisticsState = {
  statistics: <TStatisticsFromApi>{},
}
