<template>
  <div id="edit-workout" class="view">
    <div class="container">
      <WorkoutEdition
        v-if="workoutData.workout.id"
        :authUser="authUser"
        :sports="sports"
        :workout="workoutData.workout"
        :loading="workoutData.loading"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, watch, onBeforeMount } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'

  import WorkoutEdition from '@/components/Workout/WorkoutEdition.vue'
  import {
    AUTH_USER_STORE,
    SPORTS_STORE,
    WORKOUTS_STORE,
  } from '@/store/constants'
  import type { ISport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import type { IWorkoutData } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  const route = useRoute()
  const store = useStore()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const sports: ComputedRef<ISport[]> = computed(
    () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
  )
  const workoutData: ComputedRef<IWorkoutData> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT_DATA]
  )

  onBeforeMount(() => {
    store.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, {
      workoutId: route.params.workoutId,
    })
  })

  watch(
    () => route.params.workoutId,
    async (newWorkoutId) => {
      if (!newWorkoutId) {
        store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
      }
    }
  )
</script>
