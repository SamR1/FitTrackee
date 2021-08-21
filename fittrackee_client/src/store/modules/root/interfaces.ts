import { ActionContext } from 'vuex'

import { ROOT_STORE } from '@/store/constants'

export interface IAppStatistics {
  sports: number
  uploads_dir_size: number
  users: number
  workouts: number
}

export interface IAppConfig {
  federation_enabled: boolean
  gpx_limit_import: number | null
  is_registration_enabled: boolean
  map_attribution: string
  max_single_file_size: number | null
  max_users: number | null
  max_zip_file_size: number | null
}

export interface IApplication {
  statistics: IAppStatistics
  config: IAppConfig
}

export interface IRootState {
  root: boolean
  language: string
  errorMessages: string | string[] | null
  application: IApplication
  appLoading: boolean
}

export interface IRootActions {
  [ROOT_STORE.ACTIONS.GET_APPLICATION_CONFIG](
    context: ActionContext<IRootState, IRootState>
  ): void
}

export interface IRootGetters {
  [ROOT_STORE.GETTERS.APP_CONFIG](state: IRootState): IAppConfig
  [ROOT_STORE.GETTERS.APP_LOADING](state: IRootState): boolean
  [ROOT_STORE.GETTERS.ERROR_MESSAGES](
    state: IRootState
  ): string | string[] | null
  [ROOT_STORE.GETTERS.LANGUAGE](state: IRootState): string
}
