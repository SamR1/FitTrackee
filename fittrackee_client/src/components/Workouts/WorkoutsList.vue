<template>
  <div class="workouts-list">
    <Card :without-title="true">
      <template #content>
        <div class="workouts-table">
          <table>
            <thead>
              <tr>
                <th class="sport-col" />
                <th>{{ capitalize(t('workouts.WORKOUT', 1)) }}</th>
                <th>{{ capitalize(t('workouts.DATE')) }}</th>
                <th>{{ capitalize(t('workouts.DISTANCE')) }}</th>
                <th>{{ capitalize(t('workouts.DURATION')) }}</th>
                <th>{{ capitalize(t('workouts.AVE_SPEED')) }}</th>
                <th>{{ capitalize(t('workouts.MAX_SPEED')) }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="workout in workouts" :key="workout.id">
                <td class="sport-col">
                  <span class="cell-heading">
                    {{ t('workouts.SPORT', 1) }}
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
                    {{ capitalize(t('workouts.WORKOUT', 1)) }}
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
                    {{ t('workouts.DATE') }}
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
                    {{ t('workouts.DISTANCE') }}
                  </span>
                  {{ Number(workout.distance).toFixed(2) }} km
                </td>
                <td class="text-right">
                  <span class="cell-heading">
                    {{ t('workouts.DURATION') }}
                  </span>
                  {{ workout.moving }}
                </td>
                <td class="text-right">
                  <span class="cell-heading">
                    {{ t('workouts.AVE_SPEED') }}
                  </span>
                  {{ workout.ave_speed }} km/h
                </td>
                <td class="text-right">
                  <span class="cell-heading">
                    {{ t('workouts.MAX_SPEED') }}
                  </span>
                  {{ workout.max_speed }} km/h
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </Card>
    <div v-if="moreWorkoutsExist" class="more-workouts">
      <button @click="loadMoreWorkouts">
        {{ t('workouts.LOAD_MORE_WORKOUT') }}
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
    onBeforeMount,
  } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import SportImage from '@/components/Common/SportImage/index.vue'
  import StaticMap from '@/components/Common/StaticMap.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { ITranslatedSport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { capitalize } from '@/utils'
  import { getDateWithTZ } from '@/utils/dates'

  export default defineComponent({
    name: 'WorkoutsList',
    components: {
      Card,
      SportImage,
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
      const { t } = useI18n()
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
        t,
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

    ::v-deep(.card) {
      .card-content {
        .workouts-table {
          /* responsive table, adapted from: */
          /* https://uglyduck.ca/making-tables-responsive-with-minimal-css/ */
          table {
            width: 100%;
            padding: $default-padding;
            font-size: 0.9em;
            border-collapse: collapse;

            thead th {
              vertical-align: center;
              padding: $default-padding;
              border-bottom: 2px solid var(--card-border-color);
            }

            tbody {
              font-size: 0.95em;
              td {
                padding: $default-padding;
                border-bottom: 1px solid var(--card-border-color);
              }
              tr:last-child td {
                border: none;
              }
            }

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
              }
            }

            .workout-title:hover .static-map {
              display: block;
            }

            .cell-heading {
              background: var(--cell-heading-bg-color);
              color: var(--cell-heading-color);
              display: none;
              font-size: 10px;
              font-weight: bold;
              padding: 5px;
              position: absolute;
              text-transform: uppercase;
              top: 0;
              left: 0;
            }

            .sport-img {
              height: 20px;
              width: 20px;
            }
          }

          @media screen and (max-width: $small-limit) {
            table {
              thead {
                left: -9999px;
                position: absolute;
                visibility: hidden;
              }

              tr {
                border-bottom: 0;
                display: flex;
                flex-direction: row;
                flex-wrap: wrap;
                margin-bottom: 40px;
              }

              td {
                border: 1px solid var(--card-border-color);
                margin: 0 -1px -1px 0;
                padding-top: 25px !important;
                position: relative;
                text-align: center;
                width: 45%;
              }

              tbody {
                tr:last-child td {
                  border: 1px solid var(--card-border-color);
                }
              }

              .sport-col {
                display: flex;
                justify-content: center;
                padding: $default-padding;
              }
              .cell-heading {
                display: flex;
              }
              .workout-title {
                max-width: initial;
              }
            }
          }
          @media screen and (max-width: $x-small-limit) {
            table {
              td {
                width: 100%;
              }
            }
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
