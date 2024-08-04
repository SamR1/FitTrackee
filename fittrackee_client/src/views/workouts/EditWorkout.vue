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
  import useAuthUser from '@/composables/useAuthUser'
  import useSports from '@/composables/useSports'
  import { WORKOUTS_STORE } from '@/store/constants'
  import type { IWorkoutData } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  const route = useRoute()
  const store = useStore()

  const { authUser } = useAuthUser()
  const { sports } = useSports()

  const workoutData: ComputedRef<IWorkoutData> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT_DATA]
  )

  watch(
    () => route.params.workoutId,
    async (newWorkoutId) => {
      if (!newWorkoutId) {
        store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
      }
    }
  )

  onBeforeMount(() => {
    store.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, {
      workoutId: route.params.workoutId,
    })
  })
</script>
