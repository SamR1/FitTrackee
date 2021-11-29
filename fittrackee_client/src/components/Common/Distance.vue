<template>
  <span class="distance" :class="{ strong }">{{ convertedDistance }}</span>
  {{ ' ' }}
  <span v-if="displayUnit" class="unit" :class="{ strong }">
    {{ unitTo }}{{ speed ? '/h' : '' }}
  </span>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, toRefs, withDefaults } from 'vue'

  import { TUnit } from '@/types/units'
  import { units, convertDistance } from '@/utils/units'

  interface Props {
    distance: number
    unitFrom: TUnit
    useImperialUnits: boolean
    digits?: number
    displayUnit?: boolean
    speed?: boolean
    strong?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    digits: 2,
    displayUnit: true,
    speed: false,
    strong: false,
  })

  const {
    digits,
    displayUnit,
    distance,
    speed,
    strong,
    unitFrom,
    useImperialUnits,
  } = toRefs(props)
  const unitTo: ComputedRef<TUnit> = computed(() =>
    useImperialUnits.value
      ? units[unitFrom.value].defaultTarget
      : unitFrom.value
  )
  const convertedDistance = computed(() =>
    useImperialUnits.value
      ? convertDistance(
          distance.value,
          unitFrom.value,
          unitTo.value,
          digits.value
        )
      : parseFloat(distance.value.toFixed(digits.value))
  )
</script>

<style lang="scss" scoped>
  .strong {
    font-weight: bold;
  }
</style>
