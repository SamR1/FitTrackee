import { USER_STORE } from '@/store/constants'

export interface IUserState {
  authToken: string | null
}

export interface IUserGetters {
  [USER_STORE.GETTERS.IS_AUTHENTICATED](state: IUserState): boolean
}
