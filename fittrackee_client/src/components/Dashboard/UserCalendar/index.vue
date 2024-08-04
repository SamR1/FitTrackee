<template>
  <div id="user-calendar">
    <div class="section-title">{{ $t('workouts.MY_WORKOUTS') }}</div>
    <div class="calendar-card box">
      <CalendarHeader
        :day="day"
        :locale-options="locale"
        @displayNextMonth="displayNextMonth"
        @displayPreviousMonth="displayPreviousMonth"
      />
      <CalendarDays
        :start-date="calendarDates.start"
        :locale-options="locale"
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
  import { addMonths, format, subMonths } from 'date-fns'
  import { computed, ref, toRefs, onBeforeMount } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import CalendarCells from '@/components/Dashboard/UserCalendar/CalendarCells.vue'
  import CalendarDays from '@/components/Dashboard/UserCalendar/CalendarDays.vue'
  import CalendarHeader from '@/components/Dashboard/UserCalendar/CalendarHeader.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { WORKOUTS_STORE } from '@/store/constants'
  import type { ISport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import type { IWorkout, TWorkoutsPayload } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getCalendarStartAndEnd } from '@/utils/dates'
  import { defaultOrder } from '@/utils/workouts'

  interface Props {
    sports: ISport[]
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { sports, user } = toRefs(props)

  const store = useStore()

  const { locale } = useApp()
  const { isAuthUserSuspended } = useAuthUser()

  const dateFormat = 'yyyy-MM-dd'

  const day: Ref<Date> = ref(new Date())
  const calendarDates: Ref<Record<string, Date>> = ref(
    getCalendarStartAndEnd(day.value, user.value.weekm)
  )

  const calendarWorkouts: ComputedRef<IWorkout[]> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.CALENDAR_WORKOUTS]
  )

  function getCalendarWorkouts() {
    if (!isAuthUserSuspended.value) {
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
  }
  function displayNextMonth() {
    day.value = addMonths(day.value, 1)
    getCalendarWorkouts()
  }
  function displayPreviousMonth() {
    day.value = subMonths(day.value, 1)
    getCalendarWorkouts()
  }

  onBeforeMount(() => getCalendarWorkouts())
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
