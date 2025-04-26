import { enUS } from 'date-fns/locale'
import type { MutationTree } from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import type { IRootState, TRootMutations } from '@/store/modules/root/types'
import type { TAppConfig, IAppStatistics } from '@/types/application'
import type { TLanguage } from '@/types/locales'
import type { IAuthUserProfile } from '@/types/user'
import { localeFromLanguage } from '@/utils/locales'

export const mutations: MutationTree<IRootState> & TRootMutations = {
  [ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES](state: IRootState) {
    state.errorMessages = null
  },
  [ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES](
    state: IRootState,
    errorMessages: string | string[]
  ) {
    state.errorMessages = errorMessages
  },
  [ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_CONFIG](
    state: IRootState,
    config: TAppConfig
  ) {
    state.application.config = config
  },
  [ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_LOADING](
    state: IRootState,
    loading: boolean
  ) {
    state.appLoading = loading
  },
  [ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_PRIVACY_POLICY](
    state: IRootState,
    appConfig: TAppConfig
  ) {
    state.application.config.privacy_policy = appConfig.privacy_policy
    state.application.config.privacy_policy_date = appConfig.privacy_policy_date
  },
  [ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_STATS](
    state: IRootState,
    statistics: IAppStatistics
  ) {
    state.application.statistics = statistics
  },
  [ROOT_STORE.MUTATIONS.UPDATE_LANG](state: IRootState, language: TLanguage) {
    if (language in localeFromLanguage) {
      state.language = language
      state.locale = localeFromLanguage[language]
    } else {
      state.language = 'en'
      state.locale = enUS
    }
  },
  [ROOT_STORE.MUTATIONS.UPDATE_DARK_MODE](
    state: IRootState,
    darkMode: boolean | null
  ) {
    state.darkMode = darkMode
  },
  [ROOT_STORE.MUTATIONS.UPDATE_DISPLAY_OPTIONS](
    state: IRootState,
    authUser: IAuthUserProfile
  ) {
    state.application.displayOptions = {
      ...state.application.displayOptions,
      dateFormat: authUser.date_format,
      displayAscent: authUser.display_ascent,
      timezone: authUser.timezone,
      useImperialUnits: authUser.imperial_units,
    }
  },
}
