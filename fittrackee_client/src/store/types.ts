import { TAuthUserStoreModule } from '@/store/modules/authUser/types'
import { TNotificationsStoreModule } from '@/store/modules/notifications/types'
import { TOAuth2StoreModule } from '@/store/modules/oauth2/types'
import { TRootStoreModule } from '@/store/modules/root/types'
import { TSportsStoreModule } from '@/store/modules/sports/types'
import { TStatisticsStoreModule } from '@/store/modules/statistics/types'
import { TUsersStoreModule } from '@/store/modules/users/types'
import { TWorkoutsStoreModule } from '@/store/modules/workouts/types'

type StoreModules = {
  authUserModule: TAuthUserStoreModule
  notificationsModule: TNotificationsStoreModule
  oauth2Module: TOAuth2StoreModule
  rootModule: TRootStoreModule
  sportsModule: TSportsStoreModule
  statsModule: TStatisticsStoreModule
  usersModule: TUsersStoreModule
  workoutsModule: TWorkoutsStoreModule
}

export type Store = TAuthUserStoreModule<Pick<StoreModules, 'authUserModule'>> &
  TNotificationsStoreModule<Pick<StoreModules, 'notificationsModule'>> &
  TOAuth2StoreModule<Pick<StoreModules, 'oauth2Module'>> &
  TSportsStoreModule<Pick<StoreModules, 'sportsModule'>> &
  TStatisticsStoreModule<Pick<StoreModules, 'statsModule'>> &
  TWorkoutsStoreModule<Pick<StoreModules, 'workoutsModule'>> &
  TUsersStoreModule<Pick<StoreModules, 'usersModule'>> &
  TRootStoreModule<Pick<StoreModules, 'rootModule'>>
