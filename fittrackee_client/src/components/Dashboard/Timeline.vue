<template>
  <div id="timeline">
    <div class="section-title">{{ $t('workouts.LATEST_WORKOUTS') }}</div>
    <div v-if="authUser.nb_workouts > 0 && workouts.length === 0">
      <WorkoutCard
        v-for="index in [...Array(initWorkoutsCount).keys()]"
        :user="authUser"
        :useImperialUnits="authUser.imperial_units"
        :dateFormat="dateFormat"
        :timezone="authUser.timezone"
        :key="index"
      />
    </div>
    <div v-else>
      <WorkoutCard
        v-for="workout in workouts"
        :workout="workout"
        :sport="
          workouts.length > 0
            ? sports.filter((s) => s.id === workout.sport_id)[0]
            : null
        "
        :user="workout.user"
        :useImperialUnits="authUser.imperial_units"
        :dateFormat="dateFormat"
        :timezone="authUser.timezone"
        :key="workout.id"
      />
      <NoWorkouts v-if="workouts.length === 0" />
      <div v-if="moreWorkoutsExist" class="more-workouts">
        <button @click="loadMoreWorkouts">
          {{ $t('workouts.LOAD_MORE_WORKOUT') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, onBeforeMount, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import NoWorkouts from '@/components/Workouts/NoWorkouts.vue'
  import {
    AUTH_USER_STORE,
    ROOT_STORE,
    WORKOUTS_STORE,
  } from '@/store/constants'
  import type { ISport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import type { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getDateFormat } from '@/utils/dates'
  import { defaultOrder } from '@/utils/workouts'

  interface Props {
    sports: ISport[]
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { sports, authUser } = toRefs(props)

  const store = useStore()

  const page = ref(1)
  const per_page = 5
  const initWorkoutsCount =
    authUser.value.nb_workouts >= per_page
      ? per_page
      : authUser.value.nb_workouts
  const workouts: ComputedRef<IWorkout[]> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.TIMELINE_WORKOUTS]
  )
  const moreWorkoutsExist: ComputedRef<boolean> = computed(() =>
    workouts.value.length > 0
      ? workouts.value[workouts.value.length - 1].previous_workout !== null
      : false
  )
  const appLanguage: ComputedRef<string> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
  )
  const dateFormat: ComputedRef<string> = computed(() =>
    getDateFormat(authUser.value.date_format, appLanguage.value)
  )
  const isSuspended: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_SUSPENDED]
  )

  onBeforeMount(() => loadWorkouts())

  function loadWorkouts() {
    if (!isSuspended.value) {
      store.dispatch(WORKOUTS_STORE.ACTIONS.GET_TIMELINE_WORKOUTS, {
        page: page.value,
        per_page,
        ...defaultOrder,
      })
    }
  }
  function loadMoreWorkouts() {
    if (!isSuspended.value) {
      page.value += 1
      store.dispatch(WORKOUTS_STORE.ACTIONS.GET_MORE_TIMELINE_WORKOUTS, {
        page: page.value,
        per_page,
        ...defaultOrder,
      })
    }
  }
</script>

<style lang="scss" scoped>
  #timeline {
    margin-bottom: 20px;

    .more-workouts {
      display: flex;
      justify-content: center;
    }
  }
</style>
