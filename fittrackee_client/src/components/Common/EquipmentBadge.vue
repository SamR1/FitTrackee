<template>
  <router-link
    class="equipment-badge"
    :class="{ inactive: !equipment.is_active }"
    :to="{
      name: 'Equipment',
      params: { id: equipment.id },
      query: { fromWorkoutId: workoutId, fromSportId: sportId?.toString() },
    }"
  >
    <EquipmentTypeImage
      :title="$t(`equipment_types.${equipment.equipment_type.label}.LABEL`)"
      :equipment-type-label="equipment.equipment_type.label"
    />
    <span>
      {{ equipment.label }}
      {{ equipment.is_active ? '' : `(${$t('common.INACTIVE')})` }}
    </span>
  </router-link>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { IEquipment } from '@/types/equipments'

  interface Props {
    equipment: IEquipment
    workoutId?: string | null
    sportId?: Number | null
  }
  const props = defineProps<Props>()
  const { equipment, sportId, workoutId } = toRefs(props)
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  .equipment-badge {
    display: flex;
    align-items: center;
    gap: $default-padding;
    border: solid 1px var(--card-border-color);
    border-radius: $border-radius;
    padding: $default-padding * 0.5 $default-padding;

    &.inactive {
      font-style: italic;
    }
    .equipment-type-img {
      height: 25px;
      min-width: 25px;
      margin: 0;
    }
  }
</style>
