<template>
  <div id="workout">
    <div class="workout-loading" v-if="workout.loading">
      <div class="loading">
        <Loader />
      </div>
    </div>
    <div v-else class="container">
      <div v-if="workout.workout.id">
        <WorkoutDetail
          v-if="sports.length > 0"
          :workout="workout"
          :sports="sports"
          :authUser="authUser"
        />
      </div>
      <div class="container" v-else>
        <NotFound target="WORKOUT" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { computed, ComputedRef, defineComponent, onBeforeMount } from 'vue'
  import { useRoute } from 'vue-router'

  import Loader from '@/components/Common/Loader.vue'
  import NotFound from '@/components/Common/NotFound.vue'
  import WorkoutDetail from '@/components/Workout/WorkoutDetail/index.vue'
  import { SPORTS_STORE, USER_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkoutState } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'Workout',
    components: {
      Loader,
      NotFound,
      WorkoutDetail,
    },
    setup() {
      const route = useRoute()
      const store = useStore()
      onBeforeMount(() =>
        store.dispatch(
          WORKOUTS_STORE.ACTIONS.GET_WORKOUT,
          route.params.workoutId
        )
      )

      const workout: ComputedRef<IWorkoutState> = computed(
        () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT]
      )
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      const sports = computed(() => store.getters[SPORTS_STORE.GETTERS.SPORTS])

      return { authUser, sports, workout }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #workout {
    .workout-loading {
      height: $app-height;

      .loading {
        display: flex;
        align-items: center;
        height: 100%;
      }
    }
  }
</style>
