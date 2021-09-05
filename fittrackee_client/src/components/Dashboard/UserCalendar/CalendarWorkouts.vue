<template>
  <div class="calendar-workouts">
    <div v-for="(workout, index) in workouts.slice(0, 6)" :key="index">
      <CalendarWorkout
        :workout="workout"
        :sportImg="getSportImg(workout, sports)"
      />
    </div>
    <div v-if="workouts.length > 6">
      <i
        class="fa calendar-more"
        :class="`fa-${isHidden ? 'plus' : 'times'}`"
        aria-hidden="true"
        title="show more workouts"
        @click="displayMore"
      />
      <div v-if="!isHidden" class="more-workouts">
        <div
          v-for="(workout, index) in workouts.slice(6 - workouts.length)"
          :key="index"
        >
          <CalendarWorkout
            :workout="workout"
            :sportImg="getSportImg(workout, sports)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent, ref } from 'vue'

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
      const isHidden = ref(true)
      function getSportImg(workout: IWorkout, sports: ISport[]): string {
        return sports
          .filter((sport) => sport.id === workout.sport_id)
          .map((sport) => sport.img)[0]
      }
      function displayMore() {
        isHidden.value = !isHidden.value
      }
      return { isHidden, getSportImg, displayMore }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
  .calendar-workouts {
    display: flex;
    flex-wrap: wrap;
    position: relative;

    .calendar-more {
      position: absolute;
      top: 30px;
      right: -3px;
    }
    .more-workouts {
      background: whitesmoke;

      border-radius: 4px;
      box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2),
        0 6px 20px 0 rgba(0, 0, 0, 0.19);
      position: absolute;
      top: 52px;
      left: 0;
      min-width: 53px;

      margin-bottom: 20px;
      padding: 10px 15px;

      display: flex;
      flex-wrap: wrap;
      z-index: 1000;
    }
  }
</style>
