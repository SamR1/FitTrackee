import type { GetterTree } from 'vuex'

import { EQUIPMENT_TYPES_STORE } from '@/store/constants'
import type {
  IEquipmentTypesGetters,
  IEquipmentTypesState,
} from '@/store/modules/equipmentTypes/types'
import type { IRootState } from '@/store/modules/root/types'

export const getters: GetterTree<IEquipmentTypesState, IRootState> &
  IEquipmentTypesGetters = {
  [EQUIPMENT_TYPES_STORE.GETTERS.EQUIPMENT_TYPES]: (
    state: IEquipmentTypesState
  ) => state.equipmentsTypes,
}
