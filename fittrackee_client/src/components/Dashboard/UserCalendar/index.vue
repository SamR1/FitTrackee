<template>
  <div id="user-calendar">
    <div class="calendar-card box">
      <CalendarHeader
        :day="day"
        :locale-options="localeOptions"
        @displayNextMonth="displayNextMonth"
        @displayPreviousMonth="displayPreviousMonth"
      />
      <CalendarDays
        :start-date="calendarDates.start"
        :locale-options="localeOptions"
      />
      <CalendarCells
        :currentDay="day"
        :displayHARecord="user.display_ascent"
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

<script setup lang="ts">
  import { Locale, addMonths, format, subMonths } from 'date-fns'
  import { ComputedRef, computed, ref, toRefs, onBeforeMount } from 'vue'

  import CalendarCells from '@/components/Dashboard/UserCalendar/CalendarCells.vue'
  import CalendarDays from '@/components/Dashboard/UserCalendar/CalendarDays.vue'
  import CalendarHeader from '@/components/Dashboard/UserCalendar/CalendarHeader.vue'
  import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkout, TWorkoutsPayload } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getCalendarStartAndEnd } from '@/utils/dates'
  import { defaultOrder } from '@/utils/workouts'

  interface Props {
    sports: ISport[]
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()

  const { sports, user } = toRefs(props)
  const dateFormat = 'yyyy-MM-dd'
  const day = ref(new Date())
  const calendarDates = ref(getCalendarStartAndEnd(day.value, user.value.weekm))
  const calendarWorkouts: ComputedRef<IWorkout[]> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.CALENDAR_WORKOUTS]
  )
  const localeOptions: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )

  onBeforeMount(() => getCalendarWorkouts())

  function getCalendarWorkouts() {
    calendarDates.value = getCalendarStartAndEnd(day.value, props.user.weekm)
    const apiParams: TWorkoutsPayload = {
      from: format(calendarDates.value.start, dateFormat),
      to: format(calendarDates.value.end, dateFormat),
      page: 1,
      per_page: 100,
      ...defaultOrder,
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
</script>

<style lang="scss">
  #user-calendar {
    .calendar-card {
      padding: 0;

      .card-content {
        padding: 0;
      }
    }
  }
</style>
