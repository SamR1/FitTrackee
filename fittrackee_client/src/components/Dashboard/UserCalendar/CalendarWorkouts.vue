<template>
  <div class="calendar-workouts">
    <div v-for="(workout, index) in workouts" :key="index">
      <CalendarWorkout
        :workout="workout"
        :sportImg="getSportImg(workout, sports)"
      />
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue'

  import CalendarWorkout from '@/components/Dashboard/UserCalendar/CalendarWorkout.vue'
  import { ISport } from '@/types/sports'
  import { IWorkout } from '@/types/workouts'

  export default defineComponent({
    name: 'CalendarWorkouts',
    components: {
      CalendarWorkout,
    },
    props: {
      workouts: {
        type: Object as PropType<IWorkout[]>,
        required: true,
      },
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
    },
    setup() {
      function getSportImg(workout: IWorkout, sports: ISport[]): string {
        return sports
          .filter((sport) => sport.id === workout.sport_id)
          .map((sport) => sport.img)[0]
      }
      return { getSportImg }
    },
  })
</script>

<style lang="scss"></style>
