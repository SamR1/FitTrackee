import type { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import router from '@/router'
import {
  AUTH_USER_STORE,
  ROOT_STORE,
  EQUIPMENTS_STORE,
} from '@/store/constants'
import type {
  IEquipmentsActions,
  IEquipmentTypesState,
} from '@/store/modules/equipments/types'
import type { IRootState } from '@/store/modules/root/types'
import type {
  IAddEquipmentPayload,
  IDeleteEquipmentPayload,
  IEquipmentTypePayload,
  IPatchEquipmentPayload,
} from '@/types/equipments'
import { handleError } from '@/utils'

export const actions: ActionTree<IEquipmentTypesState, IRootState> &
  IEquipmentsActions = {
  [EQUIPMENTS_STORE.ACTIONS.ADD_EQUIPMENT](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    payload: IAddEquipmentPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .post('equipments', {
        description: payload.description,
        equipment_type_id: payload.equipmentTypeId,
        label: payload.label,
      })
      .then((res) => {
        if (res.data.status === 'created') {
          if (res.data.data.equipments.length > 0) {
            const equipment = res.data.data.equipments[0]
            context.commit(EQUIPMENTS_STORE.MUTATIONS.ADD_EQUIPMENT, equipment)
            router.push(`/profile/equipments/${equipment.id}`)
          }
          context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [EQUIPMENTS_STORE.ACTIONS.DELETE_EQUIPMENT](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    payload: IDeleteEquipmentPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .delete(`equipments/${payload.id}${payload.force ? '?force' : ''}`)
      .then(() => {
        context.commit(EQUIPMENTS_STORE.MUTATIONS.REMOVE_EQUIPMENT, payload.id)
        router.push('/profile/equipments')
      })
      .catch((error) => handleError(context, error))
  },
  [EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENT](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    equipmentId: number
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get(`equipments/${equipmentId}`)
      .then((res) => {
        if (res.data.status === 'success') {
          if (res.data.data.equipments.length > 0) {
            context.commit(
              EQUIPMENTS_STORE.MUTATIONS.UPDATE_EQUIPMENT,
              res.data.data.equipments[0]
            )
          }
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENTS](
    context: ActionContext<IEquipmentTypesState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('equipments')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            EQUIPMENTS_STORE.MUTATIONS.SET_EQUIPMENTS,
            res.data.data.equipments
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENT_TYPES](
    context: ActionContext<IEquipmentTypesState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('equipment-types')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            EQUIPMENTS_STORE.MUTATIONS.SET_EQUIPMENT_TYPES,
            res.data.data.equipment_types
          )
          context.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING, false)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [EQUIPMENTS_STORE.ACTIONS.UPDATE_EQUIPMENT](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    payload: IPatchEquipmentPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .patch(`equipments/${payload.id}`, {
        description: payload.description,
        equipment_type_id: payload.equipmentTypeId,
        is_active: payload.isActive,
        label: payload.label,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          if (res.data.data.equipments.length > 0) {
            context.commit(
              EQUIPMENTS_STORE.MUTATIONS.UPDATE_EQUIPMENT,
              res.data.data.equipments[0]
            )
            router.push(`/profile/equipments/${payload.id}`)
          }
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [EQUIPMENTS_STORE.ACTIONS.UPDATE_EQUIPMENT_TYPE](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    payload: IEquipmentTypePayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .patch(`equipment-types/${payload.id}`, { is_active: payload.isActive })
      .then((res) => {
        if (res.data.status === 'success') {
          context.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENT_TYPES)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
}
