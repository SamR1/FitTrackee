import type { MutationTree } from 'vuex'

import { EQUIPMENTS_STORE } from '@/store/constants'
import type {
  IEquipmentTypesState,
  TEquipmentsMutations,
} from '@/store/modules/equipments/types'
import type { IEquipment, IEquipmentType } from '@/types/equipments'

export const mutations: MutationTree<IEquipmentTypesState> &
  TEquipmentsMutations = {
  [EQUIPMENTS_STORE.MUTATIONS.ADD_EQUIPMENT](
    state: IEquipmentTypesState,
    equipment: IEquipment
  ) {
    state.equipments.push(equipment)
  },
  [EQUIPMENTS_STORE.MUTATIONS.REMOVE_EQUIPMENT](
    state: IEquipmentTypesState,
    equipmentId: string
  ) {
    state.equipments = state.equipments.filter((e) => e.id != equipmentId)
  },
  [EQUIPMENTS_STORE.MUTATIONS.SET_EQUIPMENTS](
    state: IEquipmentTypesState,
    equipments: IEquipment[]
  ) {
    state.equipments = equipments
  },
  [EQUIPMENTS_STORE.MUTATIONS.SET_EQUIPMENT_TYPES](
    state: IEquipmentTypesState,
    equipmentTypes: IEquipmentType[]
  ) {
    state.equipmentTypes = equipmentTypes
  },
  [EQUIPMENTS_STORE.MUTATIONS.UPDATE_EQUIPMENT](
    state: IEquipmentTypesState,
    equipment: IEquipment
  ) {
    const equipmentIndex = state.equipments.findIndex(
      (e) => e.id === equipment.id
    )
    if (equipmentIndex !== -1) {
      state.equipments[equipmentIndex] = equipment
    }
  },
}
