<template>
  <div
    class="equipment-type-img"
    :style="{ fill: darkTheme ? '#cfd0d0' : '#2c3e50' }"
    :title="title"
  >
    <Bike v-if="equipmentTypeLabel === 'Bike'" />
    <BikeTrainer v-if="equipmentTypeLabel === 'Bike Trainer'" />
    <Board v-if="equipmentTypeLabel === 'Board'" />
    <Kayak_Boat v-if="equipmentTypeLabel === 'Kayak_Boat'" />
    <Shoes v-if="equipmentTypeLabel === 'Shoes'" />
    <Skis v-if="equipmentTypeLabel === 'Skis'" />
    <Snowshoes v-if="equipmentTypeLabel === 'Snowshoes'" />
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import Bike from '@/components/Common/Images/EquipmentTypeImage/Bike.vue'
  import BikeTrainer from '@/components/Common/Images/EquipmentTypeImage/BikeTrainer.vue'
  import Board from '@/components/Common/Images/EquipmentTypeImage/Board.vue'
  import Kayak_Boat from '@/components/Common/Images/EquipmentTypeImage/Kayak_Boat.vue'
  import Shoes from '@/components/Common/Images/EquipmentTypeImage/Shoes.vue'
  import Skis from '@/components/Common/Images/EquipmentTypeImage/Skis.vue'
  import Snowshoes from '@/components/Common/Images/EquipmentTypeImage/Snowshoes.vue'
  import useApp from '@/composables/useApp'

  interface Props {
    equipmentTypeLabel: string
    title: string
  }
  const props = defineProps<Props>()
  const { equipmentTypeLabel, title } = toRefs(props)

  const { darkTheme } = useApp()
</script>
