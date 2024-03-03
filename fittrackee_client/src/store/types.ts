import type { TAuthUserStoreModule } from '@/store/modules/authUser/types'
import type { TEquipmentTypesStoreModule } from '@/store/modules/equipments/types'
import type { TOAuth2StoreModule } from '@/store/modules/oauth2/types'
import type { TRootStoreModule } from '@/store/modules/root/types'
import type { TSportsStoreModule } from '@/store/modules/sports/types'
import type { TStatisticsStoreModule } from '@/store/modules/statistics/types'
import type { TUsersStoreModule } from '@/store/modules/users/types'
import type { TWorkoutsStoreModule } from '@/store/modules/workouts/types'

type StoreModules = {
  authUserModule: TAuthUserStoreModule
  equipmentTypesModule: TEquipmentTypesStoreModule
  oauth2Module: TOAuth2StoreModule
  rootModule: TRootStoreModule
  sportsModule: TSportsStoreModule
  statsModule: TStatisticsStoreModule
  usersModule: TUsersStoreModule
  workoutsModule: TWorkoutsStoreModule
}

export type Store = TAuthUserStoreModule<Pick<StoreModules, 'authUserModule'>> &
  TEquipmentTypesStoreModule<Pick<StoreModules, 'equipmentTypesModule'>> &
  TOAuth2StoreModule<Pick<StoreModules, 'oauth2Module'>> &
  TSportsStoreModule<Pick<StoreModules, 'sportsModule'>> &
  TStatisticsStoreModule<Pick<StoreModules, 'statsModule'>> &
  TWorkoutsStoreModule<Pick<StoreModules, 'workoutsModule'>> &
  TUsersStoreModule<Pick<StoreModules, 'usersModule'>> &
  TRootStoreModule<Pick<StoreModules, 'rootModule'>>
