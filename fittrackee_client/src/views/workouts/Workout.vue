<template>
  <div id="workout" class="view">
    <div class="container">
      <div class="workout-container" v-if="sports.length > 0">
        <div v-if="workoutData.workout.id">
          <WorkoutUser :user="workoutData.workout.user"></WorkoutUser>
          <div
            class="box suspended"
            v-if="workoutData.workout.suspended && !isWorkoutOwner"
          >
            {{ $t('workouts.SUSPENDED_BY_ADMIN') }}
          </div>
          <WorkoutDetail
            v-else
            :workoutData="workoutData"
            :sports="sports"
            :authUser="authUser"
            :markerCoordinates="markerCoordinates"
            :displaySegment="displaySegment"
            :isWorkoutOwner="isWorkoutOwner"
          />
          <WorkoutChart
            v-if="
              workoutData.workout.with_analysis &&
              workoutData.chartData.length > 0
            "
            :workoutData="workoutData"
            :authUser="authUser"
            :displaySegment="displaySegment"
            @getCoordinates="updateCoordinates"
          />
          <WorkoutContent
            v-if="!displaySegment"
            :workout-id="workoutData.workout.id"
            content-type="DESCRIPTION"
            :content="workoutData.workout.description"
            :loading="workoutData.loading"
            :allow-edition="isWorkoutOwner"
          />
          <WorkoutSegments
            v-if="!displaySegment && workoutData.workout.segments.length > 1"
            :segments="workoutData.workout.segments"
            :useImperialUnits="authUser ? authUser.imperial_units : false"
          />
          <WorkoutContent
            v-if="isWorkoutOwner && !displaySegment"
            :workout-id="workoutData.workout.id"
            content-type="NOTES"
            :content="workoutData.workout.notes"
            :loading="workoutData.loading"
          />
          <Comments
            v-if="!displaySegment"
            :workoutData="workoutData"
            :auth-user="authUser"
          />
          <div id="bottom" />
        </div>
        <div v-else>
          <NotFound
            v-if="!workoutData.loading"
            :target="displaySegment ? 'SEGMENT' : 'WORKOUT'"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, toRefs, watch, onBeforeMount, onUnmounted } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import Comments from '@/components/Comment/Comments.vue'
  import NotFound from '@/components/Common/NotFound.vue'
  import WorkoutDetail from '@/components/Workout/WorkoutDetail/index.vue'
  import WorkoutChart from '@/components/Workout/WorkoutDetail/WorkoutChart/index.vue'
  import WorkoutContent from '@/components/Workout/WorkoutDetail/WorkoutContent.vue'
  import WorkoutSegments from '@/components/Workout/WorkoutDetail/WorkoutSegments.vue'
  import WorkoutUser from '@/components/Workout/WorkoutDetail/WorkoutUser.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import useSports from '@/composables/useSports'
  import { SPORTS_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { TCoordinates } from '@/types/map'
  import type { IWorkoutData, IWorkoutPayload } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getUserName } from '@/utils/user'

  interface Props {
    displaySegment: boolean
  }
  const props = defineProps<Props>()
  const { displaySegment } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const { authUser } = useAuthUser()
  const { sports } = useSports()

  const markerCoordinates: Ref<TCoordinates> = ref({
    latitude: null,
    longitude: null,
  })

  const workoutData: ComputedRef<IWorkoutData> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT_DATA]
  )
  const isWorkoutOwner = computed(
    () =>
      getUserName(authUser.value) ===
      getUserName(workoutData.value.workout.user)
  )

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

  onBeforeMount(() => {
    const payload: IWorkoutPayload = { workoutId: route.params.workoutId }
    if (props.displaySegment) {
      payload.segmentId = route.params.segmentId
    }
    store.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, payload)
    if (sports.value.length === 0) {
      store.dispatch(SPORTS_STORE.ACTIONS.GET_SPORTS)
    }
  })
  onUnmounted(() => {
    store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #workout {
    display: flex;
    .container {
      width: 100%;
      padding: 0;
      .workout-container {
        width: 100%;

        .user-header {
          align-items: center;
          ::v-deep(.user-picture) {
            img {
              height: 50px;
              width: 50px;
            }
            .no-picture {
              font-size: 3em;
            }
          }
          ::v-deep(.user-details) {
            flex-direction: row;
          }
        }
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
