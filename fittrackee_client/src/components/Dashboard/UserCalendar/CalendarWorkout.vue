<template>
  <div class="calendar-workout">
    <img alt="workout sport logo" :src="sportImg" :title="workout.title" />
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue'

  import { IWorkout } from '@/types/workouts'

  export default defineComponent({
    name: 'CalendarWorkouts',
    props: {
      workout: {
        type: Object as PropType<IWorkout>,
        required: true,
      },
      sportImg: {
        type: String,
        required: true,
      },
    },
  })
</script>

<style lang="scss">
  .calendar-workout {
    img {
      max-width: 18px;
      max-height: 18px;
    }
  }
</style>
