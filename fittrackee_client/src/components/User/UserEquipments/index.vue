<template>
  <div id="user-equipments" v-if="translatedEquipmentTypes">
    <router-view
      :authUser="user"
      :equipments="equipments"
      :translatedEquipmentTypes="translatedEquipmentTypes"
      :isEdition="isEdition"
      :equipmentsLoading="equipmentsLoading"
    />
  </div>
</template>

<script setup lang="ts">
  import { toRefs, onUnmounted, onBeforeMount, watch } from 'vue'
  import { useRoute } from 'vue-router'

  import useEquipments from '@/composables/useEquipments'
  import { EQUIPMENTS_STORE, ROOT_STORE } from '@/store/constants'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IAuthUserProfile
    isEdition: boolean
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const { equipments, translatedEquipmentTypes, equipmentsLoading } =
    useEquipments()

  watch(
    () => route.name,
    (newName) => {
      if (newName === 'UserEquipmentsList') {
        store.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENTS)
      }
    }
  )

  onBeforeMount(() => {
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENT_TYPES)
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENTS)
  })
  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  })
</script>
