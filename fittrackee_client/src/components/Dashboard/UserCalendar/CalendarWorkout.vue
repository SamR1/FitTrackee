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
  @import '~@/scss/base';

  .calendar-workout {
    padding: 2px;
    img {
      max-width: 18px;
      max-height: 18px;
    }

    @media screen and (max-width: $small-limit) {
      img {
        max-width: 14px;
        max-height: 14px;
      }
    }
  }
</style>
