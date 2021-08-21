import { TRootStoreModule } from '@/store/modules/root/types'
import { TStatisticsStoreModule } from '@/store/modules/statistics/types'
import { TUserStoreModule } from '@/store/modules/user/types'

type StoreModules = {
  rootModule: TRootStoreModule
  statsModule: TStatisticsStoreModule
  userModule: TUserStoreModule
}

export type Store = TUserStoreModule<Pick<StoreModules, 'userModule'>> &
  TStatisticsStoreModule<Pick<StoreModules, 'statsModule'>> &
  TRootStoreModule<Pick<StoreModules, 'rootModule'>>
