<template>
  <div id="workout">
    <div class="container">
      <div class="workout-loading" v-if="workoutData.loading">
        <div class="loading">
          <Loader />
        </div>
      </div>
      <div v-else class="workout-container">
        <div v-if="workoutData.workout.id">
          <WorkoutDetail
            v-if="sports.length > 0"
            :workoutData="workoutData"
            :sports="sports"
            :authUser="authUser"
            :markerCoordinates="markerCoordinates"
          />
          <WorkoutChart
            v-if="workoutData.chartData.length > 0"
            :workoutData="workoutData"
            :authUser="authUser"
            @getCoordinates="updateCoordinates"
          />
          <WorkoutNotes :notes="workoutData.workout.notes" />
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
    ComputedRef,
    Ref,
    computed,
    defineComponent,
    ref,
    onBeforeMount,
    onUnmounted,
  } from 'vue'
  import { useRoute } from 'vue-router'

  import Loader from '@/components/Common/Loader.vue'
  import NotFound from '@/components/Common/NotFound.vue'
  import WorkoutChart from '@/components/Workout/WorkoutChart/index.vue'
  import WorkoutDetail from '@/components/Workout/WorkoutDetail/index.vue'
  import WorkoutNotes from '@/components/Workout/WorkoutNotes.vue'
  import { SPORTS_STORE, USER_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkoutData, TCoordinates } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'Workout',
    components: {
      Loader,
      NotFound,
      WorkoutChart,
      WorkoutDetail,
      WorkoutNotes,
    },
    setup() {
      const route = useRoute()
      const store = useStore()
      onBeforeMount(() =>
        store.dispatch(
          WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA,
          route.params.workoutId
        )
      )

      const workoutData: ComputedRef<IWorkoutData> = computed(
        () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT_DATA]
      )
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      const sports = computed(() => store.getters[SPORTS_STORE.GETTERS.SPORTS])
      let markerCoordinates: Ref<TCoordinates> = ref({
        latitude: null,
        longitude: null,
      })

      function updateCoordinates(coordinates: TCoordinates) {
        markerCoordinates.value = {
          latitude: coordinates.latitude,
          longitude: coordinates.longitude,
        }
      }

      onUnmounted(() => {
        store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
      })
      return {
        authUser,
        markerCoordinates,
        sports,
        workoutData,
        updateCoordinates,
      }
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
