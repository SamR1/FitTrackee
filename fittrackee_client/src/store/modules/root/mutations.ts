import { MutationTree } from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import { IRootState, TRootMutations } from '@/store/modules/root/types'
import { TAppConfig, IAppStatistics } from '@/types/application'
import { localeFromLanguage } from '@/utils/locales'

export const mutations: MutationTree<IRootState> & TRootMutations = {
  [ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES](state: IRootState) {
    state.errorMessages = null
  },
  [ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES](
    state: IRootState,
    errorMessages: string
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
  [ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_STATS](
    state: IRootState,
    statistics: IAppStatistics
  ) {
    state.application.statistics = statistics
  },
  [ROOT_STORE.MUTATIONS.UPDATE_LANG](state: IRootState, language: string) {
    state.language = language
    state.locale = localeFromLanguage[language]
  },
}
