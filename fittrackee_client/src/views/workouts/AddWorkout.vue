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

<script lang="ts">
  import { computed, defineComponent, ComputedRef } from 'vue'

  import WorkoutEdition from '@/components/Workout/WorkoutEdition.vue'
  import {
    AUTH_USER_STORE,
    SPORTS_STORE,
    WORKOUTS_STORE,
  } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IUserProfile } from '@/types/user'
  import { IWorkoutData } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'AddWorkout',
    components: {
      WorkoutEdition,
    },
    setup() {
      const store = useStore()
      const sports: ComputedRef<ISport[]> = computed(
        () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
      )
      const authUser: ComputedRef<IUserProfile> = computed(
        () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      const workoutData: ComputedRef<IWorkoutData> = computed(
        () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT_DATA]
      )
      return { authUser, sports, workoutData }
    },
  })
</script>
