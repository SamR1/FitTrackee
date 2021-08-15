import { GetterTree } from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import { IRootState, IRootGetters } from '@/store/modules/root/interfaces'

export const getters: GetterTree<IRootState, IRootState> & IRootGetters = {
  [ROOT_STORE.GETTERS.ERROR_MESSAGES]: (state: IRootState) => {
    return state.errorMessages
  },
  [ROOT_STORE.GETTERS.LANGUAGE]: (state: IRootState) => {
    return state.language
  },
}
