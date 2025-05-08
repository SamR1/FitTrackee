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
          :authUser="authUser"
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
        <WorkoutActionAppeal
          v-if="
            displayMakeAppeal && workoutObject.suspended && workout.suspension
          "
          display-suspension-message
          :action="workout.suspension"
          :workout="workout"
        />
        <div
          class="workout-map-data"
          v-if="isWorkoutOwner || !workoutObject.suspended"
        >
          <WorkoutMap
            :workoutData="workoutData"
            :markerCoordinates="markerCoordinates"
          />
          <WorkoutVisibilityEquipment
            class="desktop"
            :workout-object="workoutObject"
            :display-options="displayOptions"
          />
        </div>
        <WorkoutData
          :workoutObject="workoutObject"
          :useImperialUnits="displayOptions.useImperialUnits"
          :displayHARecord="displayOptions.displayAscent"
          :cadenceUnit="cadenceUnit"
        />
        <WorkoutVisibilityEquipment
          class="mobile"
          :workout-object="workoutObject"
          :display-options="displayOptions"
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
  import WorkoutActionAppeal from '@/components/Workout/WorkoutActionAppeal.vue'
  import WorkoutCardTitle from '@/components/Workout/WorkoutDetail/WorkoutCardTitle.vue'
  import WorkoutData from '@/components/Workout/WorkoutDetail/WorkoutData.vue'
  import WorkoutMap from '@/components/Workout/WorkoutDetail/WorkoutMap/index.vue'
  import WorkoutVisibilityEquipment from '@/components/Workout/WorkoutDetail/WorkoutVisibilityEquipment.vue'
  import { REPORTS_STORE, ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { IDisplayOptions } from '@/types/application'
  import type { TCoordinates } from '@/types/map'
  import type { ISport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import type {
    IWorkout,
    IWorkoutData,
    IWorkoutObject,
    IWorkoutSegment,
  } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { formatDate, formatWorkoutDate, getDateWithTZ } from '@/utils/dates'

  interface Props {
    authUser?: IAuthUserProfile
    displaySegment: boolean
    sport: ISport | null
    workoutData: IWorkoutData
    markerCoordinates?: TCoordinates
    isWorkoutOwner: boolean
    cadenceUnit: string
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
  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
  const reportStatus: ComputedRef<string | null> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT_STATUS]
  )
  const workoutObject = computed(() =>
    getWorkoutObject(workout.value, segment.value)
  )
  const displayMakeAppeal: ComputedRef<boolean> = computed(
    () => workout.value.suspended_at !== null && isWorkoutOwner.value
  )
  const success: ComputedRef<null | string> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.SUCCESS]
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
      analysisVisibility: workout.analysis_visibility,
      ascent: segment ? segment.ascent : workout.ascent,
      aveCadence: segment ? segment.ave_cadence : workout.ave_cadence,
      aveHr: segment ? segment.ave_hr : workout.ave_hr,
      aveSpeed: segment ? segment.ave_speed : workout.ave_speed,
      distance: segment ? segment.distance : workout.distance,
      descent: segment ? segment.descent : workout.descent,
      duration: segment ? segment.duration : workout.duration,
      equipments: segment ? null : workout.equipments,
      liked: workout.liked,
      likes_count: workout.likes_count,
      mapVisibility: workout.map_visibility,
      maxAlt: segment ? segment.max_alt : workout.max_alt,
      maxCadence: segment ? segment.max_cadence : workout.max_cadence,
      maxHr: segment ? segment.max_hr : workout.max_hr,
      maxSpeed: segment ? segment.max_speed : workout.max_speed,
      minAlt: segment ? segment.min_alt : workout.min_alt,
      moving: segment ? segment.moving : workout.moving,
      nextUrl: urls.nextUrl,
      pauses: segment ? segment.pauses : workout.pauses,
      previousUrl: urls.previousUrl,
      records: segment ? [] : workout.records,
      segmentId: segment ? segment.segment_id : null,
      suspended: workout.suspended !== undefined ? workout.suspended : false,
      title: workout.title,
      type: props.displaySegment ? 'SEGMENT' : 'WORKOUT',
      workoutDate: workoutDate.workout_date,
      weatherEnd: segment ? null : workout.weather_end,
      workoutFullDate: formatDate(
        workout.workout_date,
        displayOptions.value.timezone,
        displayOptions.value.dateFormat
      ),
      weatherStart: segment ? null : workout.weather_start,
      with_analysis: workout.with_analysis,
      with_gpx: workout.with_gpx,
      workoutId: workout.id,
      workoutTime: workoutDate.workout_time,
      workoutVisibility: workout.workout_visibility,
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
  function resetStatuses() {
    if (reportStatus.value !== null) {
      store.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
    }
    if (success.value) {
      store.commit(WORKOUTS_STORE.MUTATIONS.SET_SUCCESS, null)
    }
  }

  onUnmounted(() => resetStatuses())

  watch(
    () => route.params.segmentId,
    async (newSegmentId) => {
      segmentId.value = newSegmentId ? +newSegmentId : null
      scrollToTop()
    }
  )
  watch(
    () => route.params.workoutId,
    async (workoutId) => {
      if (workoutId) {
        displayModal.value = false
        scrollToTop()
      }
      resetStatuses()
    }
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
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
        .report-form {
          .error-message {
            font-weight: normal;
            margin: $default-margin 0;
          }
        }
      }
      .card-content {
        display: flex;
        flex-direction: row;
        .workout-map-data {
          display: flex;
          flex-direction: column;
        }
        .desktop {
          display: block;
        }
        .mobile {
          display: none;
        }
        .workout-equipments {
          display: flex;
          flex-wrap: wrap;
          gap: $default-padding;
          margin-top: $default-margin * 0.5;
        }
        .appeal {
          margin-top: $default-padding;
        }

        .appeal-button {
          padding: 0 $default-padding;
          font-size: 0.95em;
        }
        @media screen and (max-width: $medium-limit) {
          flex-direction: column;
          .workout-map-data {
            display: flex;
          }
          .desktop {
            display: none;
          }
          .mobile {
            display: block;
          }
        }
      }
    }
  }
</style>
