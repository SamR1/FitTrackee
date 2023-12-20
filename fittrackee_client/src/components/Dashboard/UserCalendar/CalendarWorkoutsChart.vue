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
          :displayHARecord="displayHARecord"
          :workout="workout"
          :sportLabel="getSportLabel(workout, sports)"
          :sportColor="getSportColor(workout, sports)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, toRefs } from 'vue'

  import CalendarWorkout from '@/components/Dashboard/UserCalendar/CalendarWorkout.vue'
  import DonutChart from '@/components/Dashboard/UserCalendar/DonutChart.vue'
  import type { ISport } from '@/types/sports'
  import type { IWorkout } from '@/types/workouts'
  import { getSportColor, getSportLabel } from '@/utils/sports'

  interface Props {
    colors: Record<number, string>
    datasets: Record<number, Record<string, number>>
    sports: ISport[]
    workouts: IWorkout[]
    displayHARecord: boolean
  }
  const props = defineProps<Props>()

  const { colors, datasets, sports, workouts } = toRefs(props)
  const isHidden = ref(true)

  function togglePane(event: Event) {
    event.stopPropagation()
    isHidden.value = !isHidden.value
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
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
        background: var(--calendar-workouts-color);
        border-radius: 4px;
        box-shadow:
          0 4px 8px 0 var(--calendar-workouts-box-shadow-0),
          0 6px 20px 0 var(--calendar-workouts-box-shadow-1);
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
