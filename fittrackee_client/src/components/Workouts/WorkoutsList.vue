<template>
  <div class="workouts-list">
    <div class="box" :class="{ 'empty-table': workouts.length === 0 }">
      <div class="total">
        <span class="total-label">
          {{ $t('common.TOTAL').toLowerCase() }}:
        </span>
        <span v-if="pagination.total">
          {{ pagination.total }}
          {{ $t('workouts.WORKOUT', pagination.total) }}
        </span>
      </div>
      <FilterSelects
        :sort="sortList"
        :order_by="orderByList"
        :query="query"
        message="workouts"
        @updateSelect="reloadWorkouts"
      />
      <div class="workouts-table responsive-table" v-if="workouts.length > 0">
        <Pagination
          class="top-pagination"
          :pagination="pagination"
          path="/workouts"
          :query="query"
        />
        <table>
          <thead :class="{ smaller: 'de' === currentLanguage }">
            <tr>
              <th class="sport-col" />
              <th>{{ capitalize($t('workouts.WORKOUT', 1)) }}</th>
              <th>{{ capitalize($t('workouts.DATE')) }}</th>
              <th>{{ capitalize($t('workouts.DISTANCE')) }}</th>
              <th>{{ capitalize($t('workouts.DURATION')) }}</th>
              <th>{{ capitalize($t('workouts.AVE_SPEED')) }}</th>
              <th>{{ capitalize($t('workouts.MAX_SPEED')) }}</th>
              <th>{{ capitalize($t('workouts.ASCENT')) }}</th>
              <th>{{ capitalize($t('workouts.DESCENT')) }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="workout in workouts" :key="workout.id">
              <td class="sport-col">
                <span class="cell-heading">
                  {{ $t('workouts.SPORT', 1) }}
                </span>
                <SportImage
                  v-if="sports.length > 0"
                  :title="
                    sports.filter((s) => s.id === workout.sport_id)[0]
                      .translatedLabel
                  "
                  :sport-label="getSportLabel(workout, sports)"
                  :color="getSportColor(workout, sports)"
                />
              </td>
              <td
                class="workout-title"
                @mouseover="onHover(workout.id)"
                @mouseleave="onHover(null)"
              >
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
                  <span class="title">{{ workout.title }}</span>
                </router-link>
                <StaticMap
                  v-if="workout.with_gpx && hoverWorkoutId === workout.id"
                  :workout="workout"
                  :display-hover="true"
                />
              </td>
              <td class="workout-date">
                <span class="cell-heading">
                  {{ $t('workouts.DATE') }}
                </span>
                <time>
                  {{
                    formatDate(
                      workout.workout_date,
                      user.timezone,
                      user.date_format
                    )
                  }}
                </time>
              </td>
              <td class="text-right">
                <span class="cell-heading">
                  {{ $t('workouts.DISTANCE') }}
                </span>
                <Distance
                  v-if="workout.distance !== null"
                  :distance="workout.distance"
                  unitFrom="km"
                  :useImperialUnits="user.imperial_units"
                />
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
                <Distance
                  v-if="workout.ave_speed !== null"
                  :distance="workout.ave_speed"
                  unitFrom="km"
                  :speed="true"
                  :useImperialUnits="user.imperial_units"
                />
              </td>
              <td class="text-right">
                <span class="cell-heading">
                  {{ $t('workouts.MAX_SPEED') }}
                </span>
                <Distance
                  v-if="workout.max_speed !== null"
                  :distance="workout.max_speed"
                  unitFrom="km"
                  :speed="true"
                  :useImperialUnits="user.imperial_units"
                />
              </td>
              <td class="text-right">
                <span class="cell-heading">
                  {{ $t('workouts.ASCENT') }}
                </span>
                <Distance
                  v-if="workout.ascent !== null"
                  :distance="workout.ascent"
                  unitFrom="m"
                  :useImperialUnits="user.imperial_units"
                />
              </td>
              <td class="text-right">
                <span class="cell-heading">
                  {{ $t('workouts.DESCENT') }}
                </span>
                <Distance
                  v-if="workout.descent !== null"
                  :distance="workout.descent"
                  unitFrom="m"
                  :useImperialUnits="user.imperial_units"
                />
              </td>
            </tr>
          </tbody>
        </table>
        <Pagination :pagination="pagination" path="/workouts" :query="query" />
      </div>
    </div>
    <NoWorkouts v-if="workouts.length === 0" />
    <div id="bottom" />
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, toRefs, watch, capitalize, onBeforeMount } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import FilterSelects from '@/components/Common/FilterSelects.vue'
  import Pagination from '@/components/Common/Pagination.vue'
  import StaticMap from '@/components/Common/StaticMap.vue'
  import NoWorkouts from '@/components/Workouts/NoWorkouts.vue'
  import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { IPagination } from '@/types/api'
  import type { ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import type { IWorkout, TWorkoutsPayload } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getQuery, sortList, workoutsPayloadKeys } from '@/utils/api'
  import { formatDate } from '@/utils/dates'
  import { getSportColor, getSportLabel } from '@/utils/sports'
  import { convertDistance } from '@/utils/units'
  import { defaultOrder } from '@/utils/workouts'

  interface Props {
    user: IAuthUserProfile
    sports: ITranslatedSport[]
  }
  const props = defineProps<Props>()

  const store = useStore()
  const route = useRoute()
  const router = useRouter()

  const { user, sports } = toRefs(props)
  const orderByList: string[] = [
    'ave_speed',
    'distance',
    'duration',
    'workout_date',
  ]
  const workouts: ComputedRef<IWorkout[]> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.USER_WORKOUTS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUTS_PAGINATION]
  )
  const currentLanguage: ComputedRef<string> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
  )
  let query: TWorkoutsPayload = getWorkoutsQuery(route.query)
  const hoverWorkoutId: Ref<string | null> = ref(null)

  onBeforeMount(() => {
    loadWorkouts(query)
  })

  function loadWorkouts(payload: TWorkoutsPayload) {
    store.dispatch(
      WORKOUTS_STORE.ACTIONS.GET_USER_WORKOUTS,
      user.value.imperial_units ? getConvertedPayload(payload) : payload
    )
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
    const workoutQuery = getQuery(
      newQuery,
      orderByList,
      defaultOrder.order_by,
      {
        defaultSort: defaultOrder.order,
      }
    )
    Object.keys(newQuery)
      .filter((k) => workoutsPayloadKeys.includes(k))
      .map((k) => {
        if (typeof newQuery[k] === 'string') {
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          workoutQuery[k] = newQuery[k]
        }
      })
    return workoutQuery
  }

  function getConvertedPayload(payload: TWorkoutsPayload): TWorkoutsPayload {
    const convertedPayload: TWorkoutsPayload = {
      ...payload,
    }
    Object.entries(convertedPayload).map((entry) => {
      if (entry[0].match('speed|distance') && entry[1]) {
        convertedPayload[entry[0]] = convertDistance(+entry[1], 'mi', 'km')
      }
    })
    return convertedPayload
  }

  function onHover(workoutId: string | null) {
    hoverWorkoutId.value = workoutId
  }

  watch(
    () => route.query,
    async (newQuery) => {
      query = getWorkoutsQuery(newQuery)
      loadWorkouts(query)
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  .workouts-list {
    display: flex;
    flex-direction: column;
    margin-bottom: 50px;
    width: 100%;

    .box {
      padding: $default-padding $default-padding * 1.5;
      @media screen and (max-width: $small-limit) {
        &.empty-table {
          display: none;
        }
      }

      .total {
        display: flex;
        gap: $default-padding * 0.5;
        .total-label {
          font-weight: bold;
        }
      }

      .top-pagination {
        display: none;

        @media screen and (max-width: $small-limit) {
          display: flex;
        }
      }
      ::v-deep(.pagination-center) {
        @media screen and (max-width: $small-limit) {
          ul {
            margin-top: 0;
          }
        }
      }

      .workouts-table {
        .smaller {
          th {
            font-size: 0.95em;
            padding: $default-padding 0;
            max-width: 100px;
          }
        }
        td {
          text-align: right;
        }
        .sport-col {
          padding: 0;
        }
        .workout-title {
          text-align: left;
          width: 100px;
          position: relative;
          .fa-map-o {
            font-size: 0.75em;
            padding-right: $default-padding * 0.5;
          }
          .nav-item {
            white-space: nowrap;
            .title {
              word-break: break-word;
              white-space: normal;
            }
          }
          .static-map {
            display: none;
            box-shadow: 3px 3px 3px 1px var(--workout-static-map-shadow-color);
          }
        }
        .workout-title:hover .static-map {
          display: block;
        }
        .sport-img {
          height: 20px;
          width: 20px;
        }
        .workout-date {
          max-width: 60px;
          text-align: left;
        }
        @media screen and (max-width: $small-limit) {
          td,
          .workout-date,
          .workout-title {
            text-align: center;
          }
          .sport-col {
            display: flex;
            justify-content: center;
            padding: $default-padding;
          }
          .workout-date {
            max-width: initial;
          }
          .workout-title {
            max-width: initial;
            width: 100%;
          }
          .workout-title:hover .static-map {
            display: none;
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
