import { AxiosError } from 'axios'
import { ActionContext } from 'vuex'

import { ROOT_STORE } from '@/store/constants'
import { IAuthUserState } from '@/store/modules/authUser/types'
import { IOAuth2State } from '@/store/modules/oauth2/types'
import { IRootState } from '@/store/modules/root/types'
import { ISportsState } from '@/store/modules/sports/types'
import { IStatisticsState } from '@/store/modules/statistics/types'
import { IUsersState } from '@/store/modules/users/types'
import { IWorkoutsState } from '@/store/modules/workouts/types'

export const getApiUrl = (): string => {
  return process.env.NODE_ENV === 'production'
    ? '/api/'
    : `${process.env.VUE_APP_API_URL}/api/`
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
  const errorMessages = !error
    ? msg
    : error.response
    ? error.response.status === 413
      ? 'file size is greater than the allowed size'
      : error.response.data.message
      ? error.response.data.message
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
