<template>
  <div id="user-calendar">
    <Card class="calendar-card">
      <template #content>
        <CalendarHeader :day="day" locale-options="enGB" />
        <CalendarDays :start-date="calendarDates.start" locale-options="enGB" />
        <CalendaCells
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
    PropType,
    defineComponent,
    onBeforeMount,
    ComputedRef,
    computed,
  } from 'vue'

  import Card from '@/components/Common/Card.vue'
  import CalendaCells from '@/components/Dashboard/UserCalendar/CalendarCells.vue'
  import CalendarDays from '@/components/Dashboard/UserCalendar/CalendarDays.vue'
  import CalendarHeader from '@/components/Dashboard/UserCalendar/CalendarHeader.vue'
  import { SPORTS_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkout, IWorkoutsPayload } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getCalendarStartAndEnd } from '@/utils/dates'

  export default defineComponent({
    name: 'UserCalendar',
    components: {
      CalendaCells,
      CalendarDays,
      CalendarHeader,
      Card,
    },
    props: {
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const store = useStore()
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
      const sports = computed(() => store.getters[SPORTS_STORE.GETTERS.SPORTS])

      onBeforeMount(() =>
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_CALENDAR_WORKOUTS, apiParams)
      )

      return { day, calendarDates, calendarWorkouts, sports }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
  #user-calendar {
    .calendar-card {
      padding: 0;
    }
  }
</style>
