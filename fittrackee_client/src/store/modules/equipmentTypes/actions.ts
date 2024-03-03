import type { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import {
  AUTH_USER_STORE,
  ROOT_STORE,
  EQUIPMENT_TYPES_STORE,
} from '@/store/constants'
import type {
  IEquipmentTypesActions,
  IEquipmentTypesState,
} from '@/store/modules/equipmentTypes/types'
import type { IRootState } from '@/store/modules/root/types'
import type { IEquipmentTypePayload } from '@/types/equipments'
import { handleError } from '@/utils'

export const actions: ActionTree<IEquipmentTypesState, IRootState> &
  IEquipmentTypesActions = {
  [EQUIPMENT_TYPES_STORE.ACTIONS.GET_EQUIPMENT_TYPES](
    context: ActionContext<IEquipmentTypesState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('equipment-types')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            EQUIPMENT_TYPES_STORE.MUTATIONS.SET_EQUIPMENT_TYPES,
            res.data.data.equipment_types
          )
          context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [EQUIPMENT_TYPES_STORE.ACTIONS.UPDATE_EQUIPMENT_TYPE](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    payload: IEquipmentTypePayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .patch(`equipment-types/${payload.id}`, { is_active: payload.isActive })
      .then((res) => {
        if (res.data.status === 'success') {
          context.dispatch(EQUIPMENT_TYPES_STORE.ACTIONS.GET_EQUIPMENT_TYPES)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
}
