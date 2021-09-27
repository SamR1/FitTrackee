<template>
  <span
    class="workout-record"
    v-if="
      workoutObject.records &&
      workoutObject.records.find((record) => record.record_type === record_type)
    "
  >
    <sup>
      <i class="fa fa-trophy" aria-hidden="true" />
    </sup>
  </span>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue'

  import { IWorkoutObject } from '@/types/workouts'
  export default defineComponent({
    name: 'WorkoutRecord',
    props: {
      workoutObject: {
        type: Object as PropType<IWorkoutObject>,
        required: true,
      },
      record_type: {
        type: String,
        required: true,
      },
    },
  })
</script>
