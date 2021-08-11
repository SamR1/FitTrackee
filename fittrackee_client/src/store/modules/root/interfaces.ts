import { ROOT_STORE } from '@/store/constants'

export interface IRootState {
  root: boolean
  language: string
  errorMessage: string | null
}

export interface IRootGetters {
  [ROOT_STORE.GETTERS.ERROR_MESSAGE](state: IRootState): string | null
}
