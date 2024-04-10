import type { Module } from 'vuex'

import { actions } from '@/store/modules/equipments/actions'
import { getters } from '@/store/modules/equipments/getters'
import { mutations } from '@/store/modules/equipments/mutations'
import { equipmentTypesState } from '@/store/modules/equipments/state'
import type { IEquipmentTypesState } from '@/store/modules/equipments/types'
import type { IRootState } from '@/store/modules/root/types'

const equipmentTypes: Module<IEquipmentTypesState, IRootState> = {
  state: equipmentTypesState,
  actions,
  getters,
  mutations,
}

export default equipmentTypes
