<template>
  <span class="pace" :class="{ strong }">{{ convertedPace }}</span>
  {{ ' ' }}
  <span v-if="displayUnit" class="unit" :class="{ strong }">
    {{ useImperialUnits ? 'min/mile' : 'min/km' }}
  </span>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import { getPace } from '@/utils/units'

  interface Props {
    pace: string
    useImperialUnits: boolean
    displayUnit?: boolean
    strong?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    displayUnit: true,
    strong: false,
  })
  const { strong, useImperialUnits, pace } = toRefs(props)

  const convertedPace: ComputedRef<string> = computed(() =>
    getPace(pace.value, useImperialUnits.value)
  )
</script>

<style lang="scss" scoped>
  .strong {
    font-weight: bold;
  }
</style>
