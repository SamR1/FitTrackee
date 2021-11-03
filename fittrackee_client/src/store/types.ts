import { TAuthUserStoreModule } from '@/store/modules/authUser/types'
import { TRootStoreModule } from '@/store/modules/root/types'
import { TSportsStoreModule } from '@/store/modules/sports/types'
import { TStatisticsStoreModule } from '@/store/modules/statistics/types'
import { TUsersStoreModule } from '@/store/modules/users/types'
import { TWorkoutsStoreModule } from '@/store/modules/workouts/types'

type StoreModules = {
  authUserModule: TAuthUserStoreModule
  rootModule: TRootStoreModule
  sportsModule: TSportsStoreModule
  statsModule: TStatisticsStoreModule
  usersModule: TUsersStoreModule
  workoutsModule: TWorkoutsStoreModule
}

export type Store = TAuthUserStoreModule<Pick<StoreModules, 'authUserModule'>> &
  TSportsStoreModule<Pick<StoreModules, 'sportsModule'>> &
  TStatisticsStoreModule<Pick<StoreModules, 'statsModule'>> &
  TWorkoutsStoreModule<Pick<StoreModules, 'workoutsModule'>> &
  TUsersStoreModule<Pick<StoreModules, 'usersModule'>> &
  TRootStoreModule<Pick<StoreModules, 'rootModule'>>
