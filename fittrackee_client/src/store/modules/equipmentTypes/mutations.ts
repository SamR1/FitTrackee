import type { MutationTree } from 'vuex'

import { EQUIPMENT_TYPES_STORE } from '@/store/constants'
import type {
  IEquipmentTypesState,
  TEquipmentTypesMutations,
} from '@/store/modules/equipmentTypes/types'
import type { IEquipmentType } from '@/types/equipments'

export const mutations: MutationTree<IEquipmentTypesState> &
  TEquipmentTypesMutations = {
  [EQUIPMENT_TYPES_STORE.MUTATIONS.SET_EQUIPMENT_TYPES](
    state: IEquipmentTypesState,
    equipmentTypes: IEquipmentType[]
  ) {
    state.equipmentsTypes = equipmentTypes
  },
}
