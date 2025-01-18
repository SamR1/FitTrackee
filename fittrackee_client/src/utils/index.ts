import { AxiosError } from 'axios'
import type { ActionContext } from 'vuex'

import {
  AUTH_USER_STORE,
  EQUIPMENTS_STORE,
  ROOT_STORE,
} from '@/store/constants'
import type { IAuthUserState } from '@/store/modules/authUser/types'
import type { IEquipmentTypesState } from '@/store/modules/equipments/types'
import type { INotificationsState } from '@/store/modules/notifications/types'
import type { IOAuth2State } from '@/store/modules/oauth2/types'
import type { IReportsState } from '@/store/modules/reports/types'
import type { IRootState } from '@/store/modules/root/types'
import type { ISportsState } from '@/store/modules/sports/types'
import type { IStatisticsState } from '@/store/modules/statistics/types'
import type { IUsersState } from '@/store/modules/users/types'
import type { IWorkoutsState } from '@/store/modules/workouts/types'
import type { IApiErrorMessage } from '@/types/api'
import type { IEquipment, IEquipmentError } from '@/types/equipments'

export const getApiUrl = (): string => {
  return import.meta.env.PROD
    ? '/api/'
    : `${import.meta.env.VITE_APP_API_URL}/api/`
}

export const handleError = (
  context:
    | ActionContext<IRootState, IRootState>
    | ActionContext<IAuthUserState, IRootState>
    | ActionContext<IEquipmentTypesState, IRootState>
    | ActionContext<INotificationsState, IRootState>
    | ActionContext<IReportsState, IRootState>
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

  const equipmentError = getEquipmentError(error, context)
  const errorMessages = equipmentError
    ? ''
    : !error
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
    equipmentError
      ? equipmentError
      : errorMessages.includes('\n')
        ? errorMessages
            .split('\n')
            .filter((m: string) => m !== '')
            .map((m: string) => `api.ERROR.${m}`)
        : `api.ERROR.${errorMessages}`
  )
}

const getEquipmentError = (
  error: AxiosError | null,
  context:
    | ActionContext<IRootState, IRootState>
    | ActionContext<IAuthUserState, IRootState>
    | ActionContext<IEquipmentTypesState, IRootState>
    | ActionContext<INotificationsState, IRootState>
    | ActionContext<IReportsState, IRootState>
    | ActionContext<IOAuth2State, IRootState>
    | ActionContext<IStatisticsState, IRootState>
    | ActionContext<ISportsState, IRootState>
    | ActionContext<IUsersState, IRootState>
    | ActionContext<IWorkoutsState, IRootState>
) => {
  if (error?.response?.data) {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const data: IEquipmentError = { ...error.response.data }
    if ('equipment_id' in data) {
      const equipments: IEquipment[] = context.getters[
        EQUIPMENTS_STORE.GETTERS.EQUIPMENTS
      ].filter((equipment: IEquipment) => equipment.id === data.equipment_id)
      return {
        equipmentId: data.equipment_id,
        equipmentLabel: equipments.length === 0 ? null : equipments[0].label,
        status: data.status,
      }
    }
  }
  return null
}

export const getDarkTheme = (darkMode: boolean | null) => {
  if (
    darkMode === null &&
    window.matchMedia('(prefers-color-scheme: dark)').matches
  ) {
    return true
  }
  return darkMode === true
}
