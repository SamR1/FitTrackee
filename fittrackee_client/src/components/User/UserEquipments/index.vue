<template>
  <div id="user-equipments" v-if="translatedEquipmentTypes">
    <router-view
      :authUser="user"
      :equipments="equipments"
      :translatedEquipmentTypes="translatedEquipmentTypes"
      :isEdition="isEdition"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs, onUnmounted, onBeforeMount } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { EQUIPMENTS_STORE, ROOT_STORE } from '@/store/constants'
  import type {
    IEquipment,
    IEquipmentType,
    ITranslatedEquipmentType,
  } from '@/types/equipments'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { translateEquipmentTypes } from '@/utils/equipments'

  interface Props {
    user: IAuthUserProfile
    isEdition: boolean
  }
  const props = defineProps<Props>()

  const store = useStore()
  const { t } = useI18n()

  const { user } = toRefs(props)

  const equipments: ComputedRef<IEquipment[]> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENTS]
  )
  const equipmentTypes: ComputedRef<IEquipmentType[]> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENT_TYPES]
  )
  const translatedEquipmentTypes: ComputedRef<ITranslatedEquipmentType[]> =
    computed(() => translateEquipmentTypes(equipmentTypes.value, t))

  onBeforeMount(() => {
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENT_TYPES)
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENTS)
  })

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  })
</script>
