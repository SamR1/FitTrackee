<template>
  <div class="calendar-cells">
    <div class="calendar-row" v-for="(row, index) in rows" :key="index">
      <div
        class="calendar-cell"
        :class="{
          'disabled-cell': !isSameMonth(day, currentDay),
          'week-end': isWeekEnd(i),
          today: isToday(day),
        }"
        v-for="(day, i) in row"
        :key="i"
      >
        <CalendarWorkouts
          :workouts="filterWorkouts(day, workouts)"
          :sports="sports"
        />
        <div class="calendar-cell-day">
          {{ format(day, 'd') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { addDays, format, isSameDay, isSameMonth, isToday } from 'date-fns'
  import { Ref, ref, toRefs, watch, onMounted } from 'vue'

  import CalendarWorkouts from '@/components/Dashboard/UserCalendar/CalendarWorkouts.vue'
  import { ISport } from '@/types/sports'
  import { IWorkout } from '@/types/workouts'
  import { getDateWithTZ } from '@/utils/dates'

  interface Props {
    currentDay: Date
    endDate: Date
    sports: ISport[]
    startDate: Date
    timezone: string
    weekStartingMonday: boolean
    workouts: IWorkout[]
  }
  const props = defineProps<Props>()

  const {
    currentDay,
    endDate,
    sports,
    startDate,
    timezone,
    weekStartingMonday,
    workouts,
  } = toRefs(props)
  const rows: Ref<Date[][]> = ref([])

  onMounted(() => getDays())

  function getDays() {
    rows.value = []
    let day = startDate.value
    while (day <= endDate.value) {
      const days: Date[] = []
      for (let i = 0; i < 7; i++) {
        days.push(day)
        day = addDays(day, 1)
      }
      rows.value.push(days)
    }
  }
  function isWeekEnd(day: number): boolean {
    return weekStartingMonday.value
      ? [5, 6].includes(day)
      : [0, 6].includes(day)
  }
  function filterWorkouts(day: Date, workouts: IWorkout[]) {
    if (workouts) {
      return workouts
        .filter((workout) =>
          isSameDay(getDateWithTZ(workout.workout_date, timezone.value), day)
        )
        .reverse()
    }
    return []
  }

  watch(
    () => props.currentDay,
    () => getDays()
  )
</script>

<style lang="scss">
  @import '~@/scss/vars.scss';
  .calendar-cells {
    display: flex;
    flex-direction: column;
    width: 100%;

    .calendar-row {
      display: flex;
      flex-wrap: wrap;
      border-top: solid 1px var(--calendar-border-color);

      .calendar-cell {
        border-right: solid 1px var(--calendar-border-color);
        height: 40px;
        flex-grow: 1;
        flex-basis: 8%;
        padding: $default-padding * 0.5 $default-padding $default-padding * 0.5
          $default-padding * 0.5;
        width: 8%;
        position: relative;

        .calendar-cell-day {
          position: absolute;
          font-size: 0.8em;
          line-height: 1;
          top: 0.5em;
          right: 0.5em;
          font-weight: bold;
        }
      }
      .calendar-cell:last-child {
        border-right: 0;
        @media screen and (max-width: $small-limit) {
          .calendar-workouts {
            .more-workouts {
              left: -45px;
            }
          }
        }
      }
      .disabled-cell {
        color: var(--app-color-light);
      }
      .week-end {
        background: var(--calendar-week-end-color);
      }
      .today {
        background: var(--calendar-today-color);
      }
    }
    @media screen and (max-width: $small-limit) {
      .calendar-row:last-child {
        .calendar-workouts {
          .more-workouts {
            top: inherit;
            bottom: 20px;
          }
        }
      }
    }
  }
</style>
