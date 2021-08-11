import { USER_STORE } from '@/store/constants'
import { IUserState } from '@/store/modules/user/interfaces'

export type TUserMutations<S = IUserState> = {
  [USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN](state: S, authToken: string): void
}
