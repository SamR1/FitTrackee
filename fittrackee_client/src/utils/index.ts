import { AxiosError } from 'axios'
import type { ActionContext } from 'vuex'

import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
import type { IAuthUserState } from '@/store/modules/authUser/types'
import type { IOAuth2State } from '@/store/modules/oauth2/types'
import type { IRootState } from '@/store/modules/root/types'
import type { ISportsState } from '@/store/modules/sports/types'
import type { IStatisticsState } from '@/store/modules/statistics/types'
import type { IUsersState } from '@/store/modules/users/types'
import type { IWorkoutsState } from '@/store/modules/workouts/types'
import type { IApiErrorMessage } from '@/types/api'

export const getApiUrl = (): string => {
  return import.meta.env.PROD
    ? '/api/'
    : `${import.meta.env.VITE_APP_API_URL}/api/`
}

export const handleError = (
  context:
    | ActionContext<IRootState, IRootState>
    | ActionContext<IAuthUserState, IRootState>
    | ActionContext<IOAuth2State, IRootState>
    | ActionContext<IStatisticsState, IRootState>
    | ActionContext<ISportsState, IRootState>
    | ActionContext<IUsersState, IRootState>
    | ActionContext<IWorkoutsState, IRootState>,
  error: AxiosError | null,
  msg = 'UNKNOWN'
): void => {
  // if request is cancelled, no error to display
  if (error && error.message === 'canceled') {
    return
  }

  const errorInfo: IApiErrorMessage | null =
    error?.response && error.response.data ? error.response.data : null

  // if stored token is blacklisted, disconnect user
  if (error?.response?.status === 401 && errorInfo?.error === 'invalid_token') {
    localStorage.removeItem('authToken')
    context.dispatch(AUTH_USER_STORE.ACTIONS.CHECK_AUTH_USER)
    return
  }

  const errorMessages = !error
    ? msg
    : error.response
    ? error.response.status === 413
      ? 'file size is greater than the allowed size'
      : errorInfo?.message
      ? errorInfo.message
      : msg
    : error.message
    ? error.message
    : msg
  context.commit(
    ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES,
    errorMessages.includes('\n')
      ? errorMessages
          .split('\n')
          .filter((m: string) => m !== '')
          .map((m: string) => `api.ERROR.${m}`)
      : `api.ERROR.${errorMessages}`
  )
}
