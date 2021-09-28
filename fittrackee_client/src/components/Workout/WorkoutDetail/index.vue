<template>
  <div class="workout-detail">
    <Modal
      v-if="displayModal"
      :title="t('common.CONFIRMATION')"
      :message="t('workouts.WORKOUT_DELETION_CONFIRMATION')"
      @confirmAction="deleteWorkout(workoutObject.workoutId)"
      @cancelAction="updateDisplayModal(false)"
    />
    <Card :without-title="false">
      <template #title>
        <WorkoutCardTitle
          :sport="sport"
          :workoutObject="workoutObject"
          @displayModal="updateDisplayModal(true)"
        />
      </template>
      <template #content>
        <WorkoutMap
          :workoutData="workoutData"
          :markerCoordinates="markerCoordinates"
        />
        <WorkoutData :workoutObject="workoutObject" />
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import {
    ComputedRef,
    PropType,
    Ref,
    computed,
    defineComponent,
    ref,
    watch,
  } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import Card from '@/components/Common/Card.vue'
  import Modal from '@/components/Common/Modal.vue'
  import WorkoutCardTitle from '@/components/Workout/WorkoutDetail/WorkoutCardTitle.vue'
  import WorkoutData from '@/components/Workout/WorkoutDetail/WorkoutData.vue'
  import WorkoutMap from '@/components/Workout/WorkoutDetail/WorkoutMap.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import {
    IWorkout,
    IWorkoutData,
    IWorkoutObject,
    IWorkoutSegment,
    TCoordinates,
  } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { formatWorkoutDate, getDateWithTZ } from '@/utils/dates'

  export default defineComponent({
    name: 'WorkoutDetail',
    components: {
      Card,
      Modal,
      WorkoutCardTitle,
      WorkoutData,
      WorkoutMap,
    },
    props: {
      authUser: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
      displaySegment: {
        type: Boolean,
        required: true,
      },
      markerCoordinates: {
        type: Object as PropType<TCoordinates>,
        required: false,
      },
      sports: {
        type: Object as PropType<ISport[]>,
      },
      workoutData: {
        type: Object as PropType<IWorkoutData>,
        required: true,
      },
    },
    setup(props) {
      const route = useRoute()
      const store = useStore()
      const { t } = useI18n()

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
            props.authUser.timezone
          )
        )
        return {
          ascent: segment ? segment.ascent : workout.ascent,
          aveSpeed: segment ? segment.ave_speed : workout.ave_speed,
          distance: segment ? segment.distance : workout.distance,
          descent: segment ? segment.descent : workout.descent,
          duration: segment ? segment.duration : workout.duration,
          maxAlt: segment ? segment.max_alt : workout.max_alt,
          maxSpeed: segment ? segment.max_speed : workout.max_speed,
          minAlt: segment ? segment.min_alt : workout.min_alt,
          moving: segment ? segment.moving : workout.moving,
          nextUrl: urls.nextUrl,
          pauses: segment ? segment.pauses : workout.pauses,
          previousUrl: urls.previousUrl,
          records: segment ? [] : workout.records,
          segmentId: segment ? segment.segment_id : null,
          title: workout.title,
          type: props.displaySegment ? 'SEGMENT' : 'WORKOUT',
          workoutDate: workoutDate.workout_date,
          weatherEnd: segment ? null : workout.weather_end,
          workoutId: workout.id,
          weatherStart: segment ? null : workout.weather_start,
          workoutTime: workoutDate.workout_time,
        }
      }
      function updateDisplayModal(value: boolean) {
        displayModal.value = value
      }
      function deleteWorkout(workoutId: string) {
        store.dispatch(WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT, {
          workoutId: workoutId,
        })
      }

      const workout: ComputedRef<IWorkout> = computed(
        () => props.workoutData.workout
      )
      let segmentId: Ref<number | null> = ref(
        route.params.workoutId ? +route.params.segmentId : null
      )
      const segment: ComputedRef<IWorkoutSegment | null> = computed(() =>
        workout.value.segments.length > 0 && segmentId.value
          ? workout.value.segments[+segmentId.value - 1]
          : null
      )
      let displayModal: Ref<boolean> = ref(false)

      watch(
        () => route.params.segmentId,
        async (newSegmentId) => {
          if (newSegmentId) {
            segmentId.value = +newSegmentId
          }
        }
      )

      return {
        sport: computed(() =>
          props.sports
            ? props.sports.find(
                (sport) => sport.id === props.workoutData.workout.sport_id
              )
            : {}
        ),
        workoutObject: computed(() =>
          getWorkoutObject(workout.value, segment.value)
        ),
        displayModal,
        t,
        deleteWorkout,
        updateDisplayModal,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  .workout-detail {
    display: flex;
    ::v-deep(.card) {
      width: 100%;
      .card-content {
        display: flex;
        flex-direction: row;
        @media screen and (max-width: $small-limit) {
          flex-direction: column;
        }
      }
    }
  }
</style>
