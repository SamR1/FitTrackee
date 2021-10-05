<template>
  <div id="user-calendar">
    <div class="calendar-card box">
      <CalendarHeader
        :day="day"
        locale-options="enGB"
        @displayNextMonth="displayNextMonth"
        @displayPreviousMonth="displayPreviousMonth"
      />
      <CalendarDays :start-date="calendarDates.start" locale-options="enGB" />
      <CalendarCells
        :currentDay="day"
        :end-date="calendarDates.end"
        :sports="sports"
        :start-date="calendarDates.start"
        :timezone="user.timezone"
        :workouts="calendarWorkouts"
        :weekStartingMonday="user.weekm"
      />
    </div>
  </div>
</template>

<script lang="ts">
  import { addMonths, format, subMonths } from 'date-fns'
  import {
    ComputedRef,
    PropType,
    computed,
    defineComponent,
    ref,
    onBeforeMount,
  } from 'vue'

  import CalendarCells from '@/components/Dashboard/UserCalendar/CalendarCells.vue'
  import CalendarDays from '@/components/Dashboard/UserCalendar/CalendarDays.vue'
  import CalendarHeader from '@/components/Dashboard/UserCalendar/CalendarHeader.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkout, IWorkoutsPayload } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getCalendarStartAndEnd } from '@/utils/dates'

  export default defineComponent({
    name: 'UserCalendar',
    components: {
      CalendarCells,
      CalendarDays,
      CalendarHeader,
    },
    props: {
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const store = useStore()

      onBeforeMount(() => getCalendarWorkouts())

      const dateFormat = 'yyyy-MM-dd'
      let day = ref(new Date())
      let calendarDates = ref(
        getCalendarStartAndEnd(day.value, props.user.weekm)
      )
      const calendarWorkouts: ComputedRef<IWorkout[]> = computed(
        () => store.getters[WORKOUTS_STORE.GETTERS.CALENDAR_WORKOUTS]
      )

      function getCalendarWorkouts() {
        calendarDates.value = getCalendarStartAndEnd(
          day.value,
          props.user.weekm
        )
        const apiParams: IWorkoutsPayload = {
          from: format(calendarDates.value.start, dateFormat),
          to: format(calendarDates.value.end, dateFormat),
          order: 'desc',
          per_page: 100,
        }
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_CALENDAR_WORKOUTS, apiParams)
      }

      function displayNextMonth() {
        day.value = addMonths(day.value, 1)
        getCalendarWorkouts()
      }
      function displayPreviousMonth() {
        day.value = subMonths(day.value, 1)
        getCalendarWorkouts()
      }

      return {
        day,
        calendarDates,
        calendarWorkouts,
        displayNextMonth,
        displayPreviousMonth,
      }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
  #user-calendar {
    .calendar-card {
      padding: 0;

      .card-content {
        padding: 0;
      }
    }
  }
</style>
