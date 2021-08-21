import { ActionContext } from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import { IAppConfig, IApplication } from '@/types/application'

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
