<template>
  <div id="edit-workout">
    <div class="container">
      <WorkoutEdition
        :authUser="authUser"
        :sports="sports"
        :workout="workoutData.workout"
        :loading="workoutData.loading"
      />
    </div>
  </div>
</template>

<script lang="ts">
  import {
    computed,
    defineComponent,
    watch,
    onBeforeMount,
    ComputedRef,
  } from 'vue'
  import { useRoute } from 'vue-router'

  import WorkoutEdition from '@/components/Workout/WorkoutEdition.vue'
  import { SPORTS_STORE, USER_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IUserProfile } from '@/types/user'
  import { IWorkoutData } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'EditWorkout',
    components: {
      WorkoutEdition,
    },
    setup() {
      const route = useRoute()
      const store = useStore()

      onBeforeMount(() => {
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, {
          workoutId: route.params.workoutId,
        })
      })

      const authUser: ComputedRef<IUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      const sports: ComputedRef<ISport[]> = computed(
        () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
      )
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

      return { authUser, sports, workoutData }
    },
  })
</script>
