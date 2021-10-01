<template>
  <div class="calendar-workouts-chart">
    <div class="workouts-chart" @click="togglePane">
      <div class="workouts-count">{{ workouts.length }}</div>
      <DonutChart :datasets="datasets" :colors="colors" />
    </div>
    <div class="workouts-pane" v-if="!isHidden">
      <div class="more-workouts" v-click-outside="togglePane">
        <i
          class="fa fa-times calendar-more"
          aria-hidden="true"
          @click="togglePane"
        />
        <CalendarWorkout
          v-for="(workout, index) in workouts"
          :key="index"
          :workout="workout"
          :sportLabel="getSportLabel(workout, sports)"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent, ref } from 'vue'

  import CalendarWorkout from '@/components/Dashboard/UserCalendar/CalendarWorkout.vue'
  import DonutChart from '@/components/Dashboard/UserCalendar/DonutChart.vue'
  import { ISport } from '@/types/sports'
  import { IWorkout } from '@/types/workouts'
  import { getSportLabel } from '@/utils/sports'

  export default defineComponent({
    name: 'CalendarWorkoutsChart',
    components: {
      CalendarWorkout,
      DonutChart,
    },
    props: {
      colors: {
        type: Object as PropType<Record<number, string>>,
        required: true,
      },
      datasets: {
        type: Object as PropType<Record<number, Record<string, number>>>,
        required: true,
      },
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
      workouts: {
        type: Object as PropType<IWorkout[]>,
        required: true,
      },
    },
    setup() {
      const isHidden = ref(true)
      function togglePane(event: Event & { target: HTMLElement }) {
        event.stopPropagation()
        isHidden.value = !isHidden.value
      }
      return { isHidden, getSportLabel, togglePane }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  .calendar-workouts-chart {
    display: flex;

    .workouts-chart {
      position: relative;
      .workouts-count {
        display: flex;
        justify-content: center;
        position: absolute;
        top: 4px;
        left: 6px;
        width: 20px;
        font-size: 1.1em;
        font-weight: bold;
      }
      @media screen and (max-width: $small-limit) {
        .workouts-count {
          top: 16px;
          left: 6px;
        }
        ::v-deep(.donut-chart) {
          padding-top: 12px;
          svg g circle {
            stroke-width: 2;
            stroke-opacity: 0.8;
          }
        }
      }
    }

    .workouts-pane {
      display: flex;
      padding-left: 40px;

      .more-workouts {
        background: whitesmoke;
        border-radius: 4px;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2),
          0 6px 20px 0 rgba(0, 0, 0, 0.19);
        position: absolute;
        top: 52px;
        left: 0;
        min-width: 60px;
        @media screen and (max-width: $small-limit) {
          min-width: 70px;
        }

        margin-bottom: 20px;
        padding: 10px 10px;

        display: flex;
        flex-wrap: wrap;
        z-index: 1000;

        .calendar-more {
          position: absolute;
          font-size: 0.9em;
          top: 5px;
          right: 5px;
        }
      }
    }
  }
</style>
