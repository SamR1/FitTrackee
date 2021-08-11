import { ActionContext } from 'vuex'
import { IFormData } from '@/interfaces'
import { USER_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/interfaces'

// DATA
export interface IAuthUserProfile {
  admin: boolean
  bio: string | null
  birth_date: string | null
  created_at: string
  email: string
  first_name: string | null
  language: string | null
  last_name: string | null
  location: string | null
  nb_sports: number
  nb_workouts: number
  picture: string | boolean
  sports_list: number[]
  timezone: string
  total_distance: number
  total_duration: string
  username: string
  weekm: boolean
}

export interface ILoginOrRegisterData {
  actionType: string
  formData: IFormData
}

// STORE
export interface IUserState {
  authToken: string | null
  authUserProfile: IAuthUserProfile
}

export interface IUserGetters {
  [USER_STORE.GETTERS.AUTH_TOKEN](state: IUserState): string | null
  [USER_STORE.GETTERS.IS_AUTHENTICATED](state: IUserState): boolean
}

export interface IUserActions {
  [USER_STORE.ACTIONS.LOGIN_OR_REGISTER](
    context: ActionContext<IUserState, IRootState>,
    data: ILoginOrRegisterData
  ): void
}
