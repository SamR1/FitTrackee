<template>
  <div class="workout-detail">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="$t('workouts.WORKOUT_DELETION_CONFIRMATION')"
      @confirmAction="deleteWorkout(workoutObject.workoutId)"
      @cancelAction="cancelDelete"
      @keydown.esc="cancelDelete"
    />
    <Card>
      <template #title>
        <WorkoutCardTitle
          v-if="sport"
          :sport="sport"
          :workoutObject="workoutObject"
          :isWorkoutOwner="isWorkoutOwner"
          @displayModal="updateDisplayModal(true)"
        />
        <ReportForm
          v-if="workoutData.currentReporting"
          :object-id="workoutObject.workoutId"
          object-type="workout"
        />
        <div
          class="report-submitted"
          v-if="reportStatus === `workout-${workoutObject.workoutId}-created`"
        >
          <div class="info-box">
            <span>
              <i class="fa fa-info-circle" aria-hidden="true" />
              {{ $t('common.REPORT_SUBMITTED') }}
            </span>
          </div>
        </div>
      </template>
      <template #content>
        <div class="workout-map-data">
          <WorkoutMap
            :workoutData="workoutData"
            :markerCoordinates="markerCoordinates"
          />
          <WorkoutData
            :workoutObject="workoutObject"
            :useImperialUnits="displayOptions.useImperialUnits"
            :displayHARecord="displayOptions.displayAscent"
          />
        </div>
        <WorkoutVisibility
          :workoutObject="workoutObject"
          :useImperialUnits="displayOptions.useImperialUnits"
          :displayHARecord="displayOptions.displayAscent"
          v-if="workoutObject.workoutVisibility"
        />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, onUnmounted, ref, toRefs, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import ReportForm from '@/components/Common/ReportForm.vue'
  import WorkoutCardTitle from '@/components/Workout/WorkoutDetail/WorkoutCardTitle.vue'
  import WorkoutData from '@/components/Workout/WorkoutDetail/WorkoutData.vue'
  import WorkoutMap from '@/components/Workout/WorkoutDetail/WorkoutMap/index.vue'
  import WorkoutVisibility from '@/components/Workout/WorkoutDetail/WorkoutVisibility.vue'
  import { REPORTS_STORE, ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { IDisplayOptions } from '@/types/application'
  import type { ISport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import type {
    IWorkout,
    IWorkoutData,
    IWorkoutObject,
    IWorkoutSegment,
    TCoordinates,
  } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { formatWorkoutDate, getDateWithTZ } from '@/utils/dates'

  interface Props {
    authUser?: IAuthUserProfile
    displaySegment: boolean
    sports: ISport[]
    workoutData: IWorkoutData
    markerCoordinates?: TCoordinates
    isWorkoutOwner: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    markerCoordinates: () => ({}) as TCoordinates,
  })

  const route = useRoute()
  const store = useStore()

  const { isWorkoutOwner, markerCoordinates, workoutData } = toRefs(props)
  const workout: ComputedRef<IWorkout> = computed(
    () => props.workoutData.workout
  )
  const segmentId: Ref<number | null> = ref(
    route.params.workoutId ? +route.params.segmentId : null
  )
  const segment: ComputedRef<IWorkoutSegment | null> = computed(() =>
    workout.value.segments.length > 0 && segmentId.value
      ? workout.value.segments[+segmentId.value - 1]
      : null
  )
  const displayModal: Ref<boolean> = ref(false)
  const sport = computed(() =>
    props.sports
      ? props.sports.find(
          (sport) => sport.id === props.workoutData.workout.sport_id
        )
      : ({} as ISport)
  )
  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
  const reportStatus: ComputedRef<string | null> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT_STATUS]
  )
  const workoutObject = computed(() =>
    getWorkoutObject(workout.value, segment.value)
  )

  function getWorkoutObjectUrl(
    workout: IWorkout,
    displaySegment: boolean,
    segmentId: number | null
  ): Record<string, string | null> {
    const previousUrl =
      displaySegment && segmentId && segmentId !== 1
        ? `/workouts/${workout.id}/segment/${segmentId - 1}`
        : !displaySegment && workout.previous_workout
          ? `/workouts/${workout.previous_workout}`
          : null
    const nextUrl =
      displaySegment && segmentId && segmentId < workout.segments.length
        ? `/workouts/${workout.id}/segment/${segmentId + 1}`
        : !displaySegment && workout.next_workout
          ? `/workouts/${workout.next_workout}`
          : null
    return {
      previousUrl,
      nextUrl,
    }
  }
  function getWorkoutObject(
    workout: IWorkout,
    segment: IWorkoutSegment | null
  ): IWorkoutObject {
    const urls = getWorkoutObjectUrl(
      workout,
      props.displaySegment,
      segmentId.value ? +segmentId.value : null
    )
    const workoutDate = formatWorkoutDate(
      getDateWithTZ(
        props.workoutData.workout.workout_date,
        displayOptions.value.timezone
      ),
      displayOptions.value.dateFormat
    )
    return {
      ascent: segment ? segment.ascent : workout.ascent,
      aveSpeed: segment ? segment.ave_speed : workout.ave_speed,
      distance: segment ? segment.distance : workout.distance,
      descent: segment ? segment.descent : workout.descent,
      duration: segment ? segment.duration : workout.duration,
      mapVisibility: segment ? null : workout.map_visibility,
      maxAlt: segment ? segment.max_alt : workout.max_alt,
      liked: workout.liked,
      likes_count: workout.likes_count,
      maxSpeed: segment ? segment.max_speed : workout.max_speed,
      minAlt: segment ? segment.min_alt : workout.min_alt,
      moving: segment ? segment.moving : workout.moving,
      nextUrl: urls.nextUrl,
      pauses: segment ? segment.pauses : workout.pauses,
      previousUrl: urls.previousUrl,
      records: segment ? [] : workout.records,
      remoteUrl: workout.remote_url,
      segmentId: segment ? segment.segment_id : null,
      title: workout.title,
      type: props.displaySegment ? 'SEGMENT' : 'WORKOUT',
      workoutDate: workoutDate.workout_date,
      weatherEnd: segment ? null : workout.weather_end,
      weatherStart: segment ? null : workout.weather_start,
      with_gpx: workout.with_gpx,
      workoutId: workout.id,
      workoutTime: workoutDate.workout_time,
      workoutVisibility: segment ? null : workout.workout_visibility,
    }
  }
  function updateDisplayModal(value: boolean) {
    displayModal.value = value
  }
  function cancelDelete() {
    updateDisplayModal(false)
  }
  function deleteWorkout(workoutId: string) {
    updateDisplayModal(false)
    store.dispatch(WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT, {
      workoutId: workoutId,
    })
  }
  function scrollToTop() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }
  function resetReportStatus() {
    if (reportStatus.value !== null) {
      store.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
    }
  }

  onUnmounted(() => resetReportStatus())

  watch(
    () => route.params.segmentId,
    async (newSegmentId) => {
      if (newSegmentId) {
        segmentId.value = +newSegmentId
        scrollToTop()
      }
    }
  )
  watch(
    () => route.params.workoutId,
    async (workoutId) => {
      if (workoutId) {
        displayModal.value = false
        scrollToTop()
      }
      resetReportStatus()
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  .workout-detail {
    display: flex;
    ::v-deep(.card) {
      margin: 0 $default-margin;
      width: 100%;
      .card-title {
        padding: $default-padding $default-padding * 1.5;
        .report-submitted {
          display: flex;
          .info-box {
            padding: $default-padding $default-padding * 2;
            margin: $default-margin * 0.5 0 0 $default-margin;
          }
        }
      }
      .card-content {
        display: flex;
        flex-direction: column;
        .workout-map-data {
          display: flex;
          flex-direction: row;
        }
        @media screen and (max-width: $medium-limit) {
          .workout-map-data {
            display: flex;
            flex-direction: column;
          }
        }
      }
    }
  }
</style>
