<template>
  <div
    class="equipment-type-img"
    :style="{ fill: darkTheme ? '#cfd0d0' : '#2c3e50' }"
    :title="title"
  >
    <Bike v-if="equipmentTypeLabel === 'Bike'" />
    <BikeTrainer v-if="equipmentTypeLabel === 'Bike Trainer'" />
    <Kayak_Boat v-if="equipmentTypeLabel === 'Kayak_Boat'" />
    <Shoes v-if="equipmentTypeLabel === 'Shoes'" />
    <Skis v-if="equipmentTypeLabel === 'Skis'" />
    <Snowshoes v-if="equipmentTypeLabel === 'Snowshoes'" />
  </div>
</template>

<script setup lang="ts">
  import { computed, type ComputedRef, toRefs } from 'vue'
  import { useStore } from 'vuex'

  import Bike from '@/components/Common/Images/EquipmentTypeImage/Bike.vue'
  import BikeTrainer from '@/components/Common/Images/EquipmentTypeImage/BikeTrainer.vue'
  import Kayak_Boat from '@/components/Common/Images/EquipmentTypeImage/Kayak_Boat.vue'
  import Shoes from '@/components/Common/Images/EquipmentTypeImage/Shoes.vue'
  import Skis from '@/components/Common/Images/EquipmentTypeImage/Skis.vue'
  import Snowshoes from '@/components/Common/Images/EquipmentTypeImage/Snowshoes.vue'
  import { ROOT_STORE } from '@/store/constants'
  import { getDarkTheme } from '@/utils'

  interface Props {
    equipmentTypeLabel: string
    title: string
  }
  const props = defineProps<Props>()

  const store = useStore()

  const darkMode: ComputedRef<boolean | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DARK_MODE]
  )
  const darkTheme: ComputedRef<boolean> = computed(() =>
    getDarkTheme(darkMode.value)
  )
  const { equipmentTypeLabel, title } = toRefs(props)
</script>
