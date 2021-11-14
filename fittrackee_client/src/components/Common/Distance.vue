<template>
  <span class="distance" :class="{ strong }">{{ convertedDistance }}</span>
  <span v-if="displayUnit" class="unit" :class="{ strong }">
    {{ unitTo }}{{ speed ? '/h' : '' }}
  </span>
</template>

<script setup lang="ts">
  import { toRefs, withDefaults } from 'vue'

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
  const unitTo: TUnit = useImperialUnits.value
    ? units[unitFrom.value].defaultTarget
    : unitFrom.value
  const convertedDistance = useImperialUnits.value
    ? convertDistance(distance.value, unitFrom.value, unitTo, digits.value)
    : distance
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  .unit {
    padding-left: $default-padding * 0.5;
  }
  .strong {
    font-weight: bold;
  }
</style>
