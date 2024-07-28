<template>
  <span
    class="workout-record"
    v-if="
      workoutObject.records &&
      workoutObject.records.find((record) => record.record_type === recordType)
    "
  >
    <sup>
      <i class="fa fa-trophy" aria-hidden="true" />
    </sup>
  </span>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { IWorkoutObject } from '@/types/workouts'

  interface Props {
    recordType: string
    workoutObject: IWorkoutObject
  }
  const props = defineProps<Props>()
  const { recordType, workoutObject } = toRefs(props)
</script>

<style lang="scss" scoped>
  .workout-record {
    sup {
      font-size: 75%;
      line-height: 0;
    }
  }
</style>
