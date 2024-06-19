import type { IStatisticsState } from '@/store/modules/statistics/types'
import type {
  TSportStatisticsFromApi,
  TStatisticsFromApi,
} from '@/types/statistics'

export const statisticsState: IStatisticsState = {
  statistics: <TStatisticsFromApi>{},
  sportStatistics: <TSportStatisticsFromApi>{},
  totalWorkouts: 0,
  loading: false,
}
