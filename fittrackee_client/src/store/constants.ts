import {
  RootActions,
  RootGetters,
  RootMutations,
} from '@/store/modules/root/enums'
import {
  UserActions,
  UserGetters,
  UserMutations,
} from '@/store/modules/user/enums'

export const ROOT_STORE = {
  ACTIONS: RootActions,
  GETTERS: RootGetters,
  MUTATIONS: RootMutations,
}

export const USER_STORE = {
  ACTIONS: UserActions,
  GETTERS: UserGetters,
  MUTATIONS: UserMutations,
}
