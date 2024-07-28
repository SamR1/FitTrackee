<template>
  <div id="add-workout" class="view">
    <div class="container">
      <WorkoutEdition
        :authUser="authUser"
        :sports="sports"
        :isCreation="true"
        :loading="workoutData.loading"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue'
  import type { ComputedRef } from 'vue'

  import WorkoutEdition from '@/components/Workout/WorkoutEdition.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import useSports from '@/composables/useSports'
  import { WORKOUTS_STORE } from '@/store/constants'
  import type { IWorkoutData } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const { authUser } = useAuthUser()
  const { sports } = useSports()

  const workoutData: ComputedRef<IWorkoutData> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT_DATA]
  )
</script>
