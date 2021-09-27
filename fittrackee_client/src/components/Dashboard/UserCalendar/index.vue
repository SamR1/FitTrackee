<template>
  <div id="user-calendar">
    <Card class="calendar-card">
      <template #content>
        <CalendarHeader :day="day" locale-options="enGB" />
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
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { format } from 'date-fns'
  import {
    ComputedRef,
    PropType,
    computed,
    defineComponent,
    onBeforeMount,
  } from 'vue'

  import Card from '@/components/Common/Card.vue'
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
      Card,
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

      onBeforeMount(() =>
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_CALENDAR_WORKOUTS, apiParams)
      )

      const dateFormat = 'yyyy-MM-dd'
      const day = new Date()
      const calendarDates = getCalendarStartAndEnd(day, props.user.weekm)
      const apiParams: IWorkoutsPayload = {
        from: format(calendarDates.start, dateFormat),
        to: format(calendarDates.end, dateFormat),
        order: 'desc',
        per_page: 100,
      }
      const calendarWorkouts: ComputedRef<IWorkout[]> = computed(
        () => store.getters[WORKOUTS_STORE.GETTERS.CALENDAR_WORKOUTS]
      )

      return { day, calendarDates, calendarWorkouts }
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
