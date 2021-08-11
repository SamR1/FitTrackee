import { ROOT_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/interfaces'

export type TRootMutations<S = IRootState> = {
  [ROOT_STORE.MUTATIONS.UPDATE_LANG](state: S, language: string): void
}
