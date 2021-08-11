import { TRootStoreModule } from '@/store/modules/root/types'
import { TUserStoreModule } from '@/store/modules/user/types'

type StoreModules = {
  rootModule: TRootStoreModule
  userModule: TUserStoreModule
}

export type Store = TUserStoreModule<Pick<StoreModules, 'userModule'>> &
  TRootStoreModule<Pick<StoreModules, 'rootModule'>>
