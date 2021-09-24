<template>
  <div class="workout-detail">
    <Card :without-title="false">
      <template #title>
        <div class="workout-previous">
          <i class="fa fa-chevron-left" aria-hidden="true" />
        </div>
        <div class="workout-card-title">
          <div class="sport-img">
            <img alt="workout sport logo" :src="sport.img" />
          </div>
          <div class="workout-title-date">
            <div class="workout-title">{{ workout.workout.title }}</div>
            <div class="workout-date">
              {{ workoutDate.workout_date }} - {{ workoutDate.workout_time }}
            </div>
          </div>
        </div>
        <div class="workout-next">
          <i class="fa fa-chevron-right" aria-hidden="true" />
        </div>
      </template>
      <template #content>
        <WorkoutMap :workout="workout" />
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent, computed } from 'vue'

  import Card from '@/components/Common/Card.vue'
  import WorkoutMap from '@/components/Workout/WorkoutDetail/WorkoutMap.vue'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkoutState } from '@/types/workouts'
  import { formatWorkoutDate, getDateWithTZ } from '@/utils/dates'

  export default defineComponent({
    name: 'WorkoutDetail',
    components: {
      Card,
      WorkoutMap,
    },
    props: {
      authUser: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
      sports: {
        type: Object as PropType<ISport[]>,
      },
      workout: {
        type: Object as PropType<IWorkoutState>,
        required: true,
      },
    },
    setup(props) {
      return {
        sport: computed(() =>
          props.sports
            ? props.sports.find(
                (sport) => sport.id === props.workout.workout.sport_id
              )
            : {}
        ),
        workoutDate: computed(() =>
          formatWorkoutDate(
            getDateWithTZ(
              props.workout.workout.workout_date,
              props.authUser.timezone
            )
          )
        ),
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  .workout-detail {
    ::v-deep(.card) {
      .card-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
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
    }
  }
</style>
