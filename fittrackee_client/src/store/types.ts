import { TRootStoreModule } from '@/store/modules/root/types'
import { TSportsStoreModule } from '@/store/modules/sports/types'
import { TStatisticsStoreModule } from '@/store/modules/statistics/types'
import { TUserStoreModule } from '@/store/modules/user/types'
import { TWorkoutsStoreModule } from '@/store/modules/workouts/types'

type StoreModules = {
  rootModule: TRootStoreModule
  sportsModule: TSportsStoreModule
  statsModule: TStatisticsStoreModule
  userModule: TUserStoreModule
  workoutsModule: TWorkoutsStoreModule
}

export type Store = TUserStoreModule<Pick<StoreModules, 'userModule'>> &
  TSportsStoreModule<Pick<StoreModules, 'sportsModule'>> &
  TStatisticsStoreModule<Pick<StoreModules, 'statsModule'>> &
  TWorkoutsStoreModule<Pick<StoreModules, 'workoutsModule'>> &
  TRootStoreModule<Pick<StoreModules, 'rootModule'>>
