<template>
  <div id="user-workouts">
    <Loader v-if="userWorkoutsLoading" />
    <template v-else>
      <div v-if="userWorkouts.length > 0">
        <div class="section-title">{{ $t('workouts.LATEST_WORKOUTS') }}</div>
        <WorkoutCard
          v-for="workout in userWorkouts"
          :workout="workout"
          :sport="sports.filter((s) => s.id === workout.sport_id)[0]"
          :user="workout.user"
          :useImperialUnits="imperialUnits"
          :dateFormat="dateFormat"
          :timezone="timezone"
          :key="workout.id"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount, onUnmounted, toRefs, watch } from 'vue'
  import type { ComputedRef } from 'vue'

  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import useAuthUser from '@/composables/useAuthUser.ts'
  import useSports from '@/composables/useSports.ts'
  import { SPORTS_STORE, USERS_STORE } from '@/store/constants'
  import type { IUserLightProfile } from '@/types/user.ts'
  import type { IWorkout } from '@/types/workouts.ts'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IUserLightProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const { dateFormat, imperialUnits, timezone } = useAuthUser()
  const { sports } = useSports()

  const store = useStore()

  const userWorkouts: ComputedRef<IWorkout[]> = computed(
    () => store.getters[USERS_STORE.GETTERS.USER_WORKOUTS]
  )
  const userWorkoutsLoading: ComputedRef<boolean> = computed(
    () => store.getters[USERS_STORE.GETTERS.USER_WORKOUTS_LOADING]
  )

  function getUserWorkouts(name: string) {
    store.dispatch(USERS_STORE.ACTIONS.GET_USER_WORKOUTS, name)
  }

  watch(
    () => user.value,
    (newUser) => {
      getUserWorkouts(newUser.username)
    }
  )

  onBeforeMount(() => {
    getUserWorkouts(user.value.username)
    if (sports.value.length === 0 && user.value.nb_workouts > 0) {
      store.dispatch(SPORTS_STORE.ACTIONS.GET_SPORTS)
    }
  })
  onUnmounted(() =>
    store.commit(USERS_STORE.MUTATIONS.UPDATE_USER_WORKOUTS, [])
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
</style>
