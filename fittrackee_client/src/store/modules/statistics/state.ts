import { IStatisticsState } from '@/store/modules/statistics/interfaces'
import { TStatisticsFromApi } from '@/types/statistics'

export const statisticsState: IStatisticsState = {
  statistics: <TStatisticsFromApi>{},
}
