import type { GetterTree } from 'vuex'

import { EQUIPMENTS_STORE } from '@/store/constants'
import type {
  IEquipmentsGetters,
  IEquipmentTypesState,
} from '@/store/modules/equipments/types'
import type { IRootState } from '@/store/modules/root/types'

export const getters: GetterTree<IEquipmentTypesState, IRootState> &
  IEquipmentsGetters = {
  [EQUIPMENTS_STORE.GETTERS.EQUIPMENTS]: (state: IEquipmentTypesState) =>
    state.equipments,
  [EQUIPMENTS_STORE.GETTERS.EQUIPMENT_TYPES]: (state: IEquipmentTypesState) =>
    state.equipmentTypes,
}
