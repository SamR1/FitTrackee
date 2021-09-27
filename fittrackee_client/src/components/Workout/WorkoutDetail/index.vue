<template>
  <div class="workout-detail">
    <Card :without-title="false">
      <template #title>
        <div
          class="workout-previous workout-arrow"
          :class="{ inactive: !workoutObject.previousUrl }"
          :title="
            workoutObject.previousUrl
              ? t(`workouts.PREVIOUS_${workoutObject.type}`)
              : t(`workouts.NO_PREVIOUS_${workoutObject.type}`)
          "
          @click="
            workoutObject.previousUrl
              ? $router.push(workoutObject.previousUrl)
              : null
          "
        >
          <i class="fa fa-chevron-left" aria-hidden="true" />
        </div>
        <div class="workout-card-title">
          <div class="sport-img">
            <img alt="workout sport logo" :src="sport.img" />
          </div>
          <div class="workout-title-date">
            <div class="workout-title" v-if="workoutObject.type === 'WORKOUT'">
              {{ workoutObject.title }}
            </div>
            <div class="workout-title" v-else>
              <router-link
                :to="{
                  name: 'Workout',
                  params: { workoutId: workoutObject.workoutId },
                }"
              >
                {{ workoutObject.title }}
              </router-link>
              —
              <span class="workout-segment">
                <i class="fa fa-map-marker" aria-hidden="true" />
                {{ t('workouts.SEGMENT') }}
                {{ workoutObject.segmentId + 1 }}
              </span>
            </div>
            <div class="workout-date">
              {{ workoutObject.workoutDate }} -
              {{ workoutObject.workoutTime }}
            </div>
          </div>
        </div>
        <div
          class="workout-next workout-arrow"
          :class="{ inactive: !workoutObject.nextUrl }"
          :title="
            workoutObject.nextUrl
              ? t(`workouts.NEXT_${workoutObject.type}`)
              : t(`workouts.NO_NEXT_${workoutObject.type}`)
          "
          @click="
            workoutObject.nextUrl ? $router.push(workoutObject.nextUrl) : null
          "
        >
          <i class="fa fa-chevron-right" aria-hidden="true" />
        </div>
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
    defineComponent,
    computed,
    ref,
    watch,
  } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import Card from '@/components/Common/Card.vue'
  import WorkoutData from '@/components/Workout/WorkoutDetail/WorkoutData.vue'
  import WorkoutMap from '@/components/Workout/WorkoutDetail/WorkoutMap.vue'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import {
    IWorkout,
    IWorkoutData,
    IWorkoutObject,
    IWorkoutSegment,
    TCoordinates,
  } from '@/types/workouts'
  import { formatWorkoutDate, getDateWithTZ } from '@/utils/dates'

  export default defineComponent({
    name: 'WorkoutDetail',
    components: {
      Card,
      WorkoutData,
      WorkoutMap,
    },
    props: {
      authUser: {
        type: Object as PropType<IAuthUserProfile>,
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
      displaySegment: {
        type: Boolean,
        required: true,
      },
    },
    setup(props) {
      const route = useRoute()
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
        t,
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
      .card-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        .workout-arrow {
          cursor: pointer;
          &.inactive {
            color: var(--disabled-color);
            cursor: default;
          }
        }

        .workout-card-title {
          display: flex;
          flex-grow: 1;
          .sport-img {
            img {
              height: 35px;
              width: 35px;
              padding: 0 $default-padding;
            }
          }
          .workout-date {
            font-size: 0.8em;
            font-weight: normal;
          }
          .workout-segment {
            font-style: italic;
            font-weight: normal;
          }
        }
      }
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
