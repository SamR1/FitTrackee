<template>
  <div id="workout" class="view">
    <div class="container">
      <div class="workout-container" v-if="sports.length > 0">
        <div v-if="workoutData.workout.id">
          <WorkoutDetail
            :workoutData="workoutData"
            :sports="sports"
            :authUser="authUser"
            :markerCoordinates="markerCoordinates"
            :displaySegment="displaySegment"
          />
          <WorkoutChart
            v-if="
              workoutData.workout.with_gpx && workoutData.chartData.length > 0
            "
            :workoutData="workoutData"
            :authUser="authUser"
            :displaySegment="displaySegment"
            @getCoordinates="updateCoordinates"
          />
          <WorkoutSegments
            v-if="!displaySegment && workoutData.workout.segments.length > 1"
            :segments="workoutData.workout.segments"
          />
          <WorkoutNotes
            v-if="!displaySegment"
            :notes="workoutData.workout.notes"
          />
          <div id="bottom" />
        </div>
        <div v-else>
          <NotFound v-if="!workoutData.loading" target="WORKOUT" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    ComputedRef,
    Ref,
    computed,
    ref,
    toRefs,
    watch,
    onBeforeMount,
    onUnmounted,
  } from 'vue'
  import { useRoute } from 'vue-router'

  import NotFound from '@/components/Common/NotFound.vue'
  import WorkoutChart from '@/components/Workout/WorkoutChart.vue'
  import WorkoutDetail from '@/components/Workout/WorkoutDetail/index.vue'
  import WorkoutNotes from '@/components/Workout/WorkoutNotes.vue'
  import WorkoutSegments from '@/components/Workout/WorkoutSegments.vue'
  import {
    AUTH_USER_STORE,
    SPORTS_STORE,
    WORKOUTS_STORE,
  } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IUserProfile } from '@/types/user'
  import { IWorkoutData, IWorkoutPayload, TCoordinates } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  interface Props {
    displaySegment: boolean
  }
  const props = defineProps<Props>()

  const route = useRoute()
  const store = useStore()

  const { displaySegment } = toRefs(props)
  const workoutData: ComputedRef<IWorkoutData> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT_DATA]
  )
  const authUser: ComputedRef<IUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const sports: ComputedRef<ISport[]> = computed(
    () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
  )
  let markerCoordinates: Ref<TCoordinates> = ref({
    latitude: null,
    longitude: null,
  })

  onBeforeMount(() => {
    const payload: IWorkoutPayload = { workoutId: route.params.workoutId }
    if (props.displaySegment) {
      payload.segmentId = route.params.segmentId
    }
    store.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, payload)
  })

  onUnmounted(() => {
    store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
  })

  function updateCoordinates(coordinates: TCoordinates) {
    markerCoordinates.value = {
      latitude: coordinates.latitude,
      longitude: coordinates.longitude,
    }
  }

  watch(
    () => route.params.workoutId,
    async (newWorkoutId) => {
      if (newWorkoutId) {
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, {
          workoutId: newWorkoutId,
        })
      }
    }
  )
  watch(
    () => route.params.segmentId,
    async (newSegmentId) => {
      if (route.params.workoutId) {
        const payload: IWorkoutPayload = {
          workoutId: route.params.workoutId,
        }
        if (newSegmentId) {
          payload.segmentId = newSegmentId
        }
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, payload)
      }
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #workout {
    display: flex;
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
