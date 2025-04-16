<template>
  <div class="workouts-list">
    <div class="box" :class="{ 'empty-table': workouts.length === 0 }">
      <div class="total">
        <div>
          <span class="total-label">
            {{ $t('common.TOTAL').toLowerCase() }}:
          </span>
          <span>
            {{ pagination.total || 0 }}
            {{ $t('workouts.WORKOUT', pagination.total || 0) }}
          </span>
        </div>
        <button
          v-if="pagination.total > 1"
          class="scroll-button"
          @click="scrollToStatistics()"
          :title="$t('common.SCROLL_DOWN')"
          id="scroll-down-button"
        >
          <i class="fa fa-chevron-down" aria-hidden="true"></i>
        </button>
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
          <thead :class="{ smaller: appLanguage === 'de' }">
            <tr>
              <th class="sport-col">
                <span class="visually-hidden">
                  {{ $t('workouts.SPORT') }}
                </span>
              </th>
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
            <tr
              v-for="(workout, index) in workouts"
              :key="workout.id"
              :class="{ 'last-workout': index === workouts.length - 1 }"
            >
              <td class="sport-col">
                <span class="cell-heading">
                  {{ $t('workouts.SPORT', 1) }}
                </span>
                <SportImage
                  v-if="translatedSports.length > 0"
                  :title="
                    translatedSports.filter((s) => s.id === workout.sport_id)[0]
                      .translatedLabel
                  "
                  :sport-label="getSportLabel(workout, translatedSports)"
                  :color="getSportColor(workout, translatedSports)"
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
                  <VisibilityIcon :visibility="workout.workout_visibility" />
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
                {{ workout.moving ? getTotalDuration(workout.moving, $t) : '' }}
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
            <template v-if="pagination.total > 1">
              <template v-for="statsKey in statsKeys" :key="statsKey">
                <tr class="stats-label" :id="`stats_${statsKey}`">
                  <td colspan="9" v-if="pagination.pages === 1">
                    {{ $t('statistics.STATISTICS') }}
                  </td>
                  <td
                    colspan="9"
                    v-else-if="
                      statsKey === 'all' &&
                      pagination.total !== workoutsStats.all.count
                    "
                  >
                    {{
                      $t(`workouts.WORKOUTS_STATISTICS.limited`, {
                        count: workoutsStats.all.count,
                      })
                    }}
                  </td>
                  <td colspan="9" v-else>
                    {{ $t(`workouts.WORKOUTS_STATISTICS.${statsKey}`) }}
                  </td>
                </tr>
                <tr
                  class="stats-cols-labels"
                  :class="{ smaller: appLanguage === 'de' }"
                >
                  <td></td>
                  <td></td>
                  <td></td>
                  <td>{{ capitalize($t('workouts.TOTAL_DISTANCE')) }}</td>
                  <td>{{ capitalize($t('workouts.TOTAL_DURATION')) }}</td>
                  <td>{{ capitalize($t('workouts.AVE_SPEED')) }}</td>
                  <td>{{ capitalize($t('workouts.MAX_SPEED')) }}</td>
                  <td>{{ capitalize($t('workouts.TOTAL_ASCENT')) }}</td>
                  <td>{{ capitalize($t('workouts.TOTAL_DESCENT')) }}</td>
                </tr>
                <tr v-if="workoutsStats[statsKey]" class="totals">
                  <td class="sport-col hide-col"></td>
                  <td class="workout-title hide-col"></td>
                  <td class="workout-date hide-col"></td>
                  <td class="text-right">
                    <span class="cell-heading">
                      {{ $t('workouts.TOTAL_DISTANCE') }}
                    </span>
                    <Distance
                      v-if="workoutsStats[statsKey].total_distance !== null"
                      :distance="workoutsStats[statsKey].total_distance"
                      unitFrom="km"
                      :useImperialUnits="user.imperial_units"
                    />
                  </td>
                  <td class="text-right">
                    <span class="cell-heading">
                      {{ $t('workouts.TOTAL_DURATION') }}
                    </span>
                    {{
                      workoutsStats[statsKey].total_duration
                        ? getTotalDuration(
                            workoutsStats[statsKey].total_duration,
                            $t
                          )
                        : ''
                    }}
                  </td>
                  <td
                    class="text-right"
                    :class="{
                      'hide-col': workoutsStats[statsKey].total_sports > 1,
                    }"
                  >
                    <span
                      class="cell-heading"
                      v-if="workoutsStats[statsKey].total_sports === 1"
                    >
                      {{ $t('workouts.AVE_SPEED') }}
                    </span>
                    <Distance
                      v-if="
                        workoutsStats[statsKey].total_sports === 1 &&
                        workoutsStats[statsKey].ave_speed !== null
                      "
                      :distance="workoutsStats[statsKey].ave_speed"
                      unitFrom="km"
                      :speed="true"
                      :useImperialUnits="user.imperial_units"
                    />
                  </td>
                  <td
                    class="text-right"
                    :class="{
                      'hide-col': workoutsStats[statsKey].total_sports > 1,
                    }"
                  >
                    <span
                      class="cell-heading"
                      v-if="workoutsStats[statsKey].total_sports === 1"
                    >
                      {{ $t('workouts.MAX_SPEED') }}
                    </span>
                    <Distance
                      v-if="
                        workoutsStats[statsKey].total_sports === 1 &&
                        workoutsStats[statsKey].max_speed !== null
                      "
                      :distance="workoutsStats[statsKey].max_speed"
                      unitFrom="km"
                      :speed="true"
                      :useImperialUnits="user.imperial_units"
                    />
                  </td>
                  <td class="text-right">
                    <span class="cell-heading">
                      {{ $t('workouts.TOTAL_ASCENT') }}
                    </span>
                    <Distance
                      v-if="workoutsStats[statsKey].total_ascent !== null"
                      :distance="workoutsStats[statsKey].total_ascent"
                      unitFrom="m"
                      :useImperialUnits="user.imperial_units"
                    />
                  </td>
                  <td class="text-right">
                    <span class="cell-heading">
                      {{ $t('workouts.TOTAL_DESCENT') }}
                    </span>
                    <Distance
                      v-if="workoutsStats[statsKey].total_descent !== null"
                      :distance="workoutsStats[statsKey].total_descent"
                      unitFrom="m"
                      :useImperialUnits="user.imperial_units"
                    />
                  </td>
                </tr>
              </template>
            </template>
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
  import {
    computed,
    ref,
    toRefs,
    watch,
    capitalize,
    onBeforeMount,
    onUnmounted,
  } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import FilterSelects from '@/components/Common/FilterSelects.vue'
  import Pagination from '@/components/Common/Pagination.vue'
  import StaticMap from '@/components/Common/StaticMap.vue'
  import NoWorkouts from '@/components/Workouts/NoWorkouts.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { EQUIPMENTS_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { IPagination } from '@/types/api'
  import type { ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import type {
    IWorkout,
    TWorkoutsPayload,
    TWorkoutsStatistics,
  } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getQuery, sortList, workoutsPayloadKeys } from '@/utils/api'
  import { formatDate } from '@/utils/dates'
  import { getTotalDuration } from '@/utils/duration.ts'
  import { getSportColor, getSportLabel } from '@/utils/sports'
  import { convertDistance } from '@/utils/units'
  import { defaultOrder } from '@/utils/workouts'

  interface Props {
    user: IAuthUserProfile
    translatedSports: ITranslatedSport[]
  }
  const props = defineProps<Props>()
  const { user, translatedSports } = toRefs(props)

  const route = useRoute()
  const router = useRouter()
  const store = useStore()

  const orderByList: string[] = [
    'ave_speed',
    'distance',
    'duration',
    'workout_date',
  ]

  const { appLanguage } = useApp()
  const { isAuthUserSuspended } = useAuthUser()

  let query: TWorkoutsPayload = getWorkoutsQuery(route.query)

  const hoverWorkoutId: Ref<string | null> = ref(null)
  const timer: Ref<ReturnType<typeof setTimeout> | undefined> = ref()

  const workouts: ComputedRef<IWorkout[]> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.AUTH_USER_WORKOUTS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUTS_PAGINATION]
  )
  const workoutsStats: ComputedRef<TWorkoutsStatistics> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUTS_STATISTICS]
  )
  const statsKeys: ComputedRef<string[]> = computed(() =>
    workoutsStats.value.all.count === workoutsStats.value.current_page.count
      ? ['all']
      : ['current_page', 'all']
  )

  function loadWorkouts(payload: TWorkoutsPayload) {
    if (!isAuthUserSuspended.value) {
      store.dispatch(
        WORKOUTS_STORE.ACTIONS.GET_AUTH_USER_WORKOUTS,
        user.value.imperial_units ? getConvertedPayload(payload) : payload
      )
    }
  }
  function reloadWorkouts(queryParam: string, queryValue: string) {
    const newQuery: LocationQuery = { ...route.query }
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
  function scrollToStatistics() {
    const stats = document.getElementById('stats_all')
    if (stats) {
      stats.scrollIntoView({ behavior: 'smooth' })
      timer.value = setTimeout(() => {
        const scrollUpBtn = document.getElementById('scroll-up-button')
        scrollUpBtn?.focus()
      }, 300)
    }
  }

  watch(
    () => route.query,
    async (newQuery) => {
      query = getWorkoutsQuery(newQuery)
      loadWorkouts(query)
    }
  )

  onBeforeMount(() => {
    loadWorkouts(query)
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENTS)
  })
  onUnmounted(() => {
    if (timer.value) {
      clearTimeout(timer.value)
    }
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_USER_WORKOUTS, [])
    store.commit(
      WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_STATISTICS,
      {} as TWorkoutsStatistics
    )
    store.commit(
      WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_PAGINATION,
      {} as IPagination
    )
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
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
        justify-content: space-between;
        align-items: center;
        .total-label {
          font-weight: bold;
        }
      }
      .scroll-button {
        display: block;
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
          th,
          td {
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
          .visibility {
            padding-left: $default-padding * 0.5;
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
        tr.last-workout td,
        tr.totals td {
          border: none;
        }
        .stats-label {
          td {
            padding-top: $default-padding * 2;
            padding-bottom: 0;
            font-size: 1.1em;
            text-transform: lowercase;
            border: none;
            text-align: left;
            font-weight: bold;
          }
        }
        .stats-cols-labels td {
          text-align: center;
          font-weight: bold;
          border-bottom: 2px solid var(--card-border-color);
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
            &.hide-col {
              display: none;
            }
          }
          .workout-date {
            max-width: initial;
          }
          .workout-title {
            max-width: initial;
            width: 45%;
          }
          .workout-title:hover .static-map {
            display: none;
          }
          .hide-col {
            display: none;
          }
          tr.last-workout td,
          tr.totals td {
            border: 1px solid var(--card-border-color);
          }
          .stats-label {
            margin-bottom: $default-margin;
            td {
              padding: 0;
              margin: 0;
              border: none;
            }
          }
          .stats-cols-labels {
            display: none;
          }
        }

        @media screen and (max-width: $x-small-limit) {
          .workout-title {
            width: 100%;
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
