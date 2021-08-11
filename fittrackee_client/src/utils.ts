import { AxiosError } from 'axios'
import { ActionContext } from 'vuex'
import { ROOT_STORE } from '@/store/constants'
import { IUserState } from '@/store/modules/user/interfaces'
import { IRootState } from '@/store/modules/root/interfaces'

export const getApiUrl = (): string => {
  return process.env.NODE_ENV === 'production'
    ? '/api'
    : 'http://localhost:5000/api'
}

export const handleError = (
  context: ActionContext<IUserState, IRootState>,
  error: AxiosError | null,
  msg = 'error.UNKNOWN'
): void => {
  const errorMessage = !error
    ? msg
    : error.response
    ? error.response.data.message
      ? error.response.data.message
      : msg
    : error.message
    ? error.message
    : msg
  context.commit(ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGE, errorMessage)
}
