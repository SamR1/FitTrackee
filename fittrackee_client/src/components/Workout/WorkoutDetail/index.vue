<template>
  <div class="workout-detail">
    <Card :without-title="false">
      <template #title>
        <div
          class="workout-previous workout-arrow"
          :class="{ inactive: !workoutData.workout.previous_workout }"
          :title="
            workoutData.workout.previous_workout
              ? t('workouts.PREVIOUS_WORKOUT')
              : t('workouts.NO_PREVIOUS_WORKOUT')
          "
          @click="
            workoutData.workout.previous_workout
              ? $router.push({
                  name: 'Workout',
                  params: { workoutId: workoutData.workout.previous_workout },
                })
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
            <div class="workout-title">{{ workoutData.workout.title }}</div>
            <div class="workout-date">
              {{ workoutDate.workout_date }} - {{ workoutDate.workout_time }}
            </div>
          </div>
        </div>
        <div
          class="workout-next workout-arrow"
          :class="{ inactive: !workoutData.workout.next_workout }"
          :title="
            workoutData.workout.next_workout
              ? t('workouts.NEXT_WORKOUT')
              : t('workouts.NO_NEXT_WORKOUT')
          "
          @click="
            workoutData.workout.next_workout
              ? $router.push({
                  name: 'Workout',
                  params: { workoutId: workoutData.workout.next_workout },
                })
              : null
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
        <WorkoutData :workout="workoutData.workout" />
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent, computed, watch } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import Card from '@/components/Common/Card.vue'
  import WorkoutData from '@/components/Workout/WorkoutDetail/WorkoutData.vue'
  import WorkoutMap from '@/components/Workout/WorkoutDetail/WorkoutMap.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkoutData, TCoordinates } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
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
    },
    setup(props) {
      const route = useRoute()
      const store = useStore()
      const { t } = useI18n()
      watch(
        () => route.params.workoutId,
        async (newWorkoutId) => {
          store.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, newWorkoutId)
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
        workoutDate: computed(() =>
          formatWorkoutDate(
            getDateWithTZ(
              props.workoutData.workout.workout_date,
              props.authUser.timezone
            )
          )
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
