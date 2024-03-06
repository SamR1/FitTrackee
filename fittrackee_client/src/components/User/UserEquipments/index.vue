<template>
  <div id="user-equipments" v-if="translatedEquipmentTypes">
    <router-view
      :equipments="equipments"
      :translatedEquipmentTypes="translatedEquipmentTypes"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, type ComputedRef, onUnmounted } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { EQUIPMENTS_STORE, ROOT_STORE } from '@/store/constants'
  import type {
    IEquipment,
    IEquipmentType,
    ITranslatedEquipmentType,
  } from '@/types/equipments'
  import { useStore } from '@/use/useStore'
  import { translateEquipmentTypes } from '@/utils/equipments'

  const store = useStore()
  const { t } = useI18n()
  const equipments: ComputedRef<IEquipment[]> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENTS]
  )
  const equipmentTypes: ComputedRef<IEquipmentType[]> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENT_TYPES]
  )
  const translatedEquipmentTypes: ComputedRef<ITranslatedEquipmentType[]> =
    computed(() => translateEquipmentTypes(equipmentTypes.value, t))

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  })
</script>
