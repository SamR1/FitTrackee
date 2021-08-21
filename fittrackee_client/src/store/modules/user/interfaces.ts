import { ActionContext } from 'vuex'

import { USER_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/interfaces'
import { IAuthUserProfile, ILoginOrRegisterData } from '@/types/user'

// STORE
export interface IUserState {
  authToken: string | null
  authUserProfile: IAuthUserProfile
}

export interface IUserActions {
  [USER_STORE.ACTIONS.CHECK_AUTH_USER](
    context: ActionContext<IUserState, IRootState>
  ): void
  [USER_STORE.ACTIONS.GET_USER_PROFILE](
    context: ActionContext<IUserState, IRootState>
  ): void
  [USER_STORE.ACTIONS.LOGIN_OR_REGISTER](
    context: ActionContext<IUserState, IRootState>,
    data: ILoginOrRegisterData
  ): void
  [USER_STORE.ACTIONS.LOGOUT](
    context: ActionContext<IUserState, IRootState>
  ): void
}

export interface IUserGetters {
  [USER_STORE.GETTERS.AUTH_TOKEN](state: IUserState): string | null
  [USER_STORE.GETTERS.AUTH_USER_PROFILE](state: IUserState): IAuthUserProfile
  [USER_STORE.GETTERS.IS_AUTHENTICATED](state: IUserState): boolean
}
