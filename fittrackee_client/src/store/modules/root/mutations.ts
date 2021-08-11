import { MutationTree } from 'vuex'
import { ROOT_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/interfaces'
import { TRootMutations } from '@/store/modules/root/types'

export const mutations: MutationTree<IRootState> & TRootMutations = {
  [ROOT_STORE.MUTATIONS.UPDATE_LANG](state: IRootState, language: string) {
    state.language = language
  },
}
