<template>
  <router-link
    class="workout-equipment"
    :to="{
      name: 'Equipment',
      params: { id: equipment.id },
      query: { fromWorkoutId: workoutId },
    }"
  >
    <EquipmentTypeImage
      :title="$t(`equipment_types.${equipment.equipment_type.label}.LABEL`)"
      :equipment-type-label="equipment.equipment_type.label"
    />
    <span>
      {{ equipment.label }}
    </span>
  </router-link>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { IEquipment } from '@/types/equipments'

  interface Props {
    equipment: IEquipment
    workoutId?: string | null
  }
  const props = defineProps<Props>()

  const { equipment, workoutId } = toRefs(props)
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  .workout-equipment {
    display: flex;
    gap: $default-padding;
    border: solid 1px var(--card-border-color);
    border-radius: $border-radius;
    padding: $default-padding * 0.5 $default-padding;

    .equipment-type-img {
      height: 25px;
      width: 25px;
      margin: 0;
    }
  }
</style>
