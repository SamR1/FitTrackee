import { ROOT_STORE } from '@/store/constants'

export interface IRootState {
  root: boolean
  language: string
  errorMessages: string | string[] | null
}

export interface IRootGetters {
  [ROOT_STORE.GETTERS.ERROR_MESSAGES](
    state: IRootState
  ): string | string[] | null
  [ROOT_STORE.GETTERS.LANGUAGE](state: IRootState): string
}
