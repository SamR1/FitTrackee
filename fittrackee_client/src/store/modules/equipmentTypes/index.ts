import type { Module } from 'vuex'

import { actions } from '@/store/modules/equipmentTypes/actions'
import { getters } from '@/store/modules/equipmentTypes/getters'
import { mutations } from '@/store/modules/equipmentTypes/mutations'
import { equipmentTypesState } from '@/store/modules/equipmentTypes/state'
import type { IEquipmentTypesState } from '@/store/modules/equipmentTypes/types'
import type { IRootState } from '@/store/modules/root/types'

const equipmentTypes: Module<IEquipmentTypesState, IRootState> = {
  state: equipmentTypesState,
  actions,
  getters,
  mutations,
}

export default equipmentTypes
