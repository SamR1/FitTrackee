<template>
  <div class="workouts-list">
    <div class="box" :class="{ 'empty-table': workouts.length === 0 }">
      <div class="workouts-table responsive-table">
        <table>
          <thead>
            <tr>
              <th class="sport-col" />
              <th>{{ capitalize($t('workouts.WORKOUT', 1)) }}</th>
              <th>{{ capitalize($t('workouts.DATE')) }}</th>
              <th>{{ capitalize($t('workouts.DISTANCE')) }}</th>
              <th>{{ capitalize($t('workouts.DURATION')) }}</th>
              <th>{{ capitalize($t('workouts.AVE_SPEED')) }}</th>
              <th>{{ capitalize($t('workouts.MAX_SPEED')) }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="workout in workouts" :key="workout.id">
              <td class="sport-col">
                <span class="cell-heading">
                  {{ $t('workouts.SPORT', 1) }}
                </span>
                <SportImage
                  :title="
                    sports.filter((s) => s.id === workout.sport_id)[0]
                      .translatedLabel
                  "
                  :sport-label="
                    sports.filter((s) => s.id === workout.sport_id)[0].label
                  "
                ></SportImage>
              </td>
              <td class="workout-title">
                <span class="cell-heading">
                  {{ capitalize($t('workouts.WORKOUT', 1)) }}
                </span>
                <router-link
                  class="nav-item"
                  :to="{ name: 'Workout', params: { workoutId: workout.id } }"
                >
                  <i
                    v-if="workout.with_gpx"
                    class="fa fa-map-o"
                    aria-hidden="true"
                  />
                  {{ workout.title }}
                </router-link>
                <StaticMap
                  v-if="workout.with_gpx"
                  :workout="workout"
                  :display-hover="true"
                />
              </td>
              <td>
                <span class="cell-heading">
                  {{ $t('workouts.DATE') }}
                </span>
                {{
                  format(
                    getDateWithTZ(workout.workout_date, user.timezone),
                    'dd/MM/yyyy HH:mm'
                  )
                }}
              </td>
              <td class="text-right">
                <span class="cell-heading">
                  {{ $t('workouts.DISTANCE') }}
                </span>
                {{ Number(workout.distance).toFixed(2) }} km
              </td>
              <td class="text-right">
                <span class="cell-heading">
                  {{ $t('workouts.DURATION') }}
                </span>
                {{ workout.moving }}
              </td>
              <td class="text-right">
                <span class="cell-heading">
                  {{ $t('workouts.AVE_SPEED') }}
                </span>
                {{ workout.ave_speed }} km/h
              </td>
              <td class="text-right">
                <span class="cell-heading">
                  {{ $t('workouts.MAX_SPEED') }}
                </span>
                {{ workout.max_speed }} km/h
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <NoWorkouts v-if="workouts.length === 0" />
    <div v-if="moreWorkoutsExist" class="more-workouts">
      <button @click="loadMoreWorkouts">
        {{ $t('workouts.LOAD_MORE_WORKOUT') }}
      </button>
    </div>
    <div id="bottom" />
  </div>
</template>

<script lang="ts">
  import { format } from 'date-fns'
  import {
    ComputedRef,
    PropType,
    computed,
    defineComponent,
    ref,
    watch,
    capitalize,
    onBeforeMount,
  } from 'vue'

  import StaticMap from '@/components/Common/StaticMap.vue'
  import NoWorkouts from '@/components/Workouts/NoWorkouts.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { ITranslatedSport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getDateWithTZ } from '@/utils/dates'

  export default defineComponent({
    name: 'WorkoutsList',
    components: {
      NoWorkouts,
      StaticMap,
    },
    props: {
      params: {
        type: Object as PropType<Record<string, string>>,
        required: true,
      },
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
      sports: {
        type: Object as PropType<ITranslatedSport[]>,
      },
    },
    setup(props) {
      const store = useStore()
      const workouts: ComputedRef<IWorkout[]> = computed(
        () => store.getters[WORKOUTS_STORE.GETTERS.USER_WORKOUTS]
      )
      const per_page = 10
      const page = ref(1)
      const moreWorkoutsExist: ComputedRef<boolean> = computed(() =>
        workouts.value.length > 0
          ? workouts.value[workouts.value.length - 1].previous_workout !== null
          : false
      )

      onBeforeMount(() => {
        loadWorkouts()
      })

      function loadWorkouts() {
        page.value = 1
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_USER_WORKOUTS, {
          page: page.value,
          per_page,
          ...props.params,
        })
      }
      function loadMoreWorkouts() {
        page.value += 1
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_MORE_USER_WORKOUTS, {
          page: page.value,
          per_page,
          ...props.params,
        })
      }

      watch(
        () => props.params,
        async () => {
          loadWorkouts()
        }
      )

      return {
        moreWorkoutsExist,
        workouts,
        capitalize,
        format,
        getDateWithTZ,
        loadMoreWorkouts,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  .workouts-list {
    display: flex;
    flex-direction: column;
    margin-bottom: 50px;
    width: 100%;

    .box {
      @media screen and (max-width: $small-limit) {
        &.empty-table {
          display: none;
        }
      }
      .workouts-table {
        .sport-col {
          padding-right: 0;
        }
        .workout-title {
          max-width: 90px;
          position: relative;
          .fa-map-o {
            font-size: 0.75em;
          }
          .static-map {
            display: none;
            box-shadow: 3px 3px 3px 1px lightgrey;
          }
        }
        .workout-title:hover .static-map {
          display: block;
        }
        .sport-img {
          height: 20px;
          width: 20px;
        }
        @media screen and (max-width: $small-limit) {
          .sport-col {
            display: flex;
            justify-content: center;
            padding: $default-padding;
          }
          .workout-title {
            max-width: initial;
          }
        }
      }
    }

    .more-workouts {
      display: flex;
      justify-content: center;
      padding: $default-padding;
    }
  }
</style>
