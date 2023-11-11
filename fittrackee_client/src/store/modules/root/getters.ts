import type { GetterTree } from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import type { IRootGetters, IRootState } from '@/store/modules/root/types'

export const getters: GetterTree<IRootState, IRootState> & IRootGetters = {
  [ROOT_STORE.GETTERS.APP_CONFIG]: (state: IRootState) => {
    return state.application.config
  },
  [ROOT_STORE.GETTERS.APP_LOADING]: (state: IRootState) => {
    return state.appLoading
  },
  [ROOT_STORE.GETTERS.APP_STATS]: (state: IRootState) => {
    return state.application.statistics
  },
  [ROOT_STORE.GETTERS.ERROR_MESSAGES]: (state: IRootState) => {
    return state.errorMessages
  },
  [ROOT_STORE.GETTERS.LANGUAGE]: (state: IRootState) => {
    return state.language
  },
  [ROOT_STORE.GETTERS.LOCALE]: (state: IRootState) => {
    return state.locale
  },
}
