<template>
  <div class="calendar-workouts">
    <div class="desktop-display">
      <div
        class="workouts-display"
        v-if="workouts.length <= displayedWorkoutCount"
      >
        <CalendarWorkout
          v-for="(workout, index) in workouts.slice(0, displayedWorkoutCount)"
          :key="index"
          :workout="workout"
          :sportLabel="getSportLabel(workout, sports)"
          :sportColor="getSportColor(workout, sports)"
        />
      </div>
      <div v-else class="donut-display">
        <CalendarWorkoutsChart
          :workouts="workouts"
          :sports="sports"
          :datasets="chartDatasets"
          :colors="colors"
        />
      </div>
    </div>
    <div class="mobile-display">
      <div class="donut-display" v-if="workouts.length > 0">
        <CalendarWorkoutsChart
          :workouts="workouts"
          :sports="sports"
          :datasets="chartDatasets"
          :colors="colors"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'

  import CalendarWorkout from '@/components/Dashboard/UserCalendar/CalendarWorkout.vue'
  import CalendarWorkoutsChart from '@/components/Dashboard/UserCalendar/CalendarWorkoutsChart.vue'
  import { ISport } from '@/types/sports'
  import { IWorkout } from '@/types/workouts'
  import { getSportColor, getSportLabel, sportIdColors } from '@/utils/sports'
  import { getDonutDatasets } from '@/utils/workouts'

  interface Props {
    workouts: IWorkout[]
    sports: ISport[]
  }
  const props = defineProps<Props>()

  const { workouts, sports } = toRefs(props)
  const chartDatasets = computed(() => getDonutDatasets(props.workouts))
  const colors = computed(() => sportIdColors(props.sports))
  const displayedWorkoutCount = 6
</script>

<style lang="scss">
  @import '~@/scss/base';
  .calendar-workouts {
    .desktop-display {
      display: flex;
    }
    .mobile-display {
      display: none;
    }

    .workouts-display {
      display: flex;
      flex-wrap: wrap;
      position: relative;
      margin: 0 $default-padding 0 0;
    }
    .donut-display {
      display: flex;
      height: 34px;
      width: 34px;
    }

    @media screen and (max-width: $small-limit) {
      .desktop-display {
        display: none;
      }
      .mobile-display {
        display: flex;
      }
    }
  }
</style>
