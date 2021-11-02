<template>
  <div class="workouts-list">
    <div class="box" :class="{ 'empty-table': workouts.length === 0 }">
      <FilterSelects
        :sort="sortList"
        :order_by="orderByList"
        :query="query"
        message="workouts"
        @updateSelect="reloadWorkouts"
      />
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
    watch,
    capitalize,
    onBeforeMount,
  } from 'vue'
  import { LocationQuery, useRoute, useRouter } from 'vue-router'

  import FilterSelects from '@/components/Common/FilterSelects.vue'
  import StaticMap from '@/components/Common/StaticMap.vue'
  import NoWorkouts from '@/components/Workouts/NoWorkouts.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { ITranslatedSport } from '@/types/sports'
  import { IUserProfile } from '@/types/user'
  import { IWorkout, TWorkoutsPayload } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getQuery, sortList, workoutsPayloadKeys } from '@/utils/api'
  import { getDateWithTZ } from '@/utils/dates'
  import { defaultOrder } from '@/utils/workouts'

  export default defineComponent({
    name: 'WorkoutsList',
    components: {
      FilterSelects,
      NoWorkouts,
      StaticMap,
    },
    props: {
      user: {
        type: Object as PropType<IUserProfile>,
        required: true,
      },
      sports: {
        type: Object as PropType<ITranslatedSport[]>,
      },
    },
    setup() {
      const store = useStore()
      const route = useRoute()
      const router = useRouter()

      const orderByList: string[] = [
        'ave_speed',
        'distance',
        'duration',
        'workout_date',
      ]
      const workouts: ComputedRef<IWorkout[]> = computed(
        () => store.getters[WORKOUTS_STORE.GETTERS.USER_WORKOUTS]
      )
      let query: TWorkoutsPayload = getWorkoutsQuery(route.query)

      onBeforeMount(() => {
        loadWorkouts(query)
      })

      function loadWorkouts(payload: TWorkoutsPayload) {
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_USER_WORKOUTS, payload)
      }
      function reloadWorkouts(queryParam: string, queryValue: string) {
        const newQuery: LocationQuery = Object.assign({}, route.query)
        newQuery[queryParam] = queryValue
        if (queryParam === 'per_page') {
          newQuery['page'] = '1'
        }
        query = getWorkoutsQuery(newQuery)
        router.push({ path: '/workouts', query })
      }

      function getWorkoutsQuery(newQuery: LocationQuery): TWorkoutsPayload {
        query = getQuery(newQuery, orderByList, defaultOrder.order_by, {
          defaultSort: defaultOrder.order,
          query,
        })
        Object.keys(newQuery)
          .filter((k) => workoutsPayloadKeys.includes(k))
          .map((k) => {
            if (typeof newQuery[k] === 'string') {
              // eslint-disable-next-line @typescript-eslint/ban-ts-comment
              // @ts-ignore
              query[k] = newQuery[k]
            }
          })
        return query
      }

      watch(
        () => route.query,
        async (newQuery) => {
          query = getWorkoutsQuery(newQuery)
          loadWorkouts(query)
        }
      )

      return {
        query,
        orderByList,
        sortList,
        workouts,
        capitalize,
        format,
        getDateWithTZ,
        reloadWorkouts,
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
