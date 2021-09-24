<template>
  <span
    class="workout-record"
    v-if="
      workout.records &&
      workout.records.find((record) => record.record_type === record_type)
    "
  >
    <sup>
      <i class="fa fa-trophy" aria-hidden="true" />
    </sup>
  </span>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue'

  import { IWorkout } from '@/types/workouts'
  export default defineComponent({
    name: 'WorkoutRecord',
    props: {
      workout: {
        type: Object as PropType<IWorkout>,
        required: true,
      },
      record_type: {
        type: String,
        required: true,
      },
    },
  })
</script>
