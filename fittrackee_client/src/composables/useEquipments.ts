import { computed } from 'vue'
import type { ComputedRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import { EQUIPMENTS_STORE } from '@/store/constants'
import type {
  IEquipment,
  IEquipmentType,
  ITranslatedEquipmentType,
} from '@/types/equipments'
import { useStore } from '@/use/useStore'
import { translateEquipmentTypes } from '@/utils/equipments'

export default function useEquipments() {
  const route = useRoute()
  const store = useStore()
  const { t } = useI18n()

  const equipment: ComputedRef<IEquipment | null> = computed(() =>
    getEquipment(equipments.value)
  )
  const equipments: ComputedRef<IEquipment[]> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENTS]
  )
  const equipmentsLoading: ComputedRef<boolean> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.LOADING]
  )
  const equipmentTypes: ComputedRef<IEquipmentType[]> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENT_TYPES]
  )
  const translatedEquipmentTypes: ComputedRef<ITranslatedEquipmentType[]> =
    computed(() => translateEquipmentTypes(equipmentTypes.value, t))

  function getEquipment(equipmentsList: IEquipment[]) {
    if (!route.params.id) {
      return null
    }
    const filteredEquipmentList = equipmentsList.filter((equipment) =>
      route.params.id ? equipment.id === route.params.id : null
    )
    if (filteredEquipmentList.length === 0) {
      return null
    }
    return filteredEquipmentList[0]
  }

  return {
    equipment,
    equipments,
    equipmentTypes,
    translatedEquipmentTypes,
    equipmentsLoading,
  }
}
