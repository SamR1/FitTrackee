<template>
  <div id="workout">
    <div class="container">
      <div class="workout-loading" v-if="workout.loading">
        <div class="loading">
          <Loader />
        </div>
      </div>
      <div v-else class="workout-container">
        <div v-if="workout.workout.id">
          <WorkoutDetail
            v-if="sports.length > 0"
            :workout="workout"
            :sports="sports"
            :authUser="authUser"
          />
          <WorkoutChart
            v-if="workout.chartData.length > 0"
            :workout="workout"
            :authUser="authUser"
          />
        </div>
        <div v-else>
          <NotFound target="WORKOUT" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import {
    computed,
    ComputedRef,
    defineComponent,
    onBeforeMount,
    onUnmounted,
  } from 'vue'
  import { useRoute } from 'vue-router'

  import Loader from '@/components/Common/Loader.vue'
  import NotFound from '@/components/Common/NotFound.vue'
  import WorkoutChart from '@/components/Workout/WorkoutChart/index.vue'
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
      WorkoutChart,
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

      onUnmounted(() => {
        store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
      })
      return { authUser, sports, workout }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #workout {
    display: flex;
    margin-bottom: 45px;
    .container {
      width: 100%;
      padding: 0;
      .workout-container {
        width: 100%;
      }
      .workout-loading {
        height: $app-height;
        width: 100%;
        .loading {
          display: flex;
          align-items: center;
          height: 100%;
        }
      }
    }
  }
</style>
