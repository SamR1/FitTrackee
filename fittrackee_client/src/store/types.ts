import type { TAuthUserStoreModule } from '@/store/modules/authUser/types'
import type { TEquipmentTypesStoreModule } from '@/store/modules/equipments/types'
import type { TNotificationsStoreModule } from '@/store/modules/notifications/types'
import type { TOAuth2StoreModule } from '@/store/modules/oauth2/types'
import type { TReportsStoreModule } from '@/store/modules/reports/types'
import type { TRootStoreModule } from '@/store/modules/root/types'
import type { TSportsStoreModule } from '@/store/modules/sports/types'
import type { TStatisticsStoreModule } from '@/store/modules/statistics/types'
import type { TUsersStoreModule } from '@/store/modules/users/types'
import type { TWorkoutsStoreModule } from '@/store/modules/workouts/types'

type StoreModules = {
  authUserModule: TAuthUserStoreModule
  equipmentTypesModule: TEquipmentTypesStoreModule
  notificationsModule: TNotificationsStoreModule
  oauth2Module: TOAuth2StoreModule
  reportsModule: TReportsStoreModule
  rootModule: TRootStoreModule
  sportsModule: TSportsStoreModule
  statsModule: TStatisticsStoreModule
  usersModule: TUsersStoreModule
  workoutsModule: TWorkoutsStoreModule
}

export type Store = TAuthUserStoreModule<Pick<StoreModules, 'authUserModule'>> &
  TEquipmentTypesStoreModule<Pick<StoreModules, 'equipmentTypesModule'>> &
  TNotificationsStoreModule<Pick<StoreModules, 'notificationsModule'>> &
  TOAuth2StoreModule<Pick<StoreModules, 'oauth2Module'>> &
  TReportsStoreModule<Pick<StoreModules, 'reportsModule'>> &
  TSportsStoreModule<Pick<StoreModules, 'sportsModule'>> &
  TStatisticsStoreModule<Pick<StoreModules, 'statsModule'>> &
  TWorkoutsStoreModule<Pick<StoreModules, 'workoutsModule'>> &
  TUsersStoreModule<Pick<StoreModules, 'usersModule'>> &
  TRootStoreModule<Pick<StoreModules, 'rootModule'>>
