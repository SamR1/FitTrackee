<template>
  <div class="stats-chart">
    <div v-if="hideChartIfNoData && emptyStats">
      {{ $t('workouts.NO_WORKOUTS') }}
    </div>
    <div v-else>
      <div class="chart-radio">
        <label>
          <input
            type="radio"
            name="total_distance"
            :checked="displayedData === 'total_distance'"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.DISTANCE') }}
        </label>
        <label>
          <input
            type="radio"
            name="total_duration"
            :checked="displayedData === 'total_duration'"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.DURATION') }}
        </label>
        <label>
          <input
            type="radio"
            name="nb_workouts"
            :checked="displayedData === 'total_workouts'"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.WORKOUT', 2) }}
        </label>
        <label v-if="fullStats">
          <input
            type="radio"
            name="average_speed"
            :checked="displayedData === 'average_speed'"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.AVERAGE_SPEED') }}
        </label>
        <label v-if="fullStats">
          <input
            type="radio"
            name="total_ascent"
            :checked="displayedData === 'total_ascent'"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.ASCENT') }}
        </label>
        <label v-if="fullStats">
          <input
            type="radio"
            name="total_descent"
            :checked="displayedData === 'total_descent'"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.DESCENT') }}
        </label>
      </div>
      <Chart
        v-if="labels.length > 0"
        :datasets="datasets"
        :labels="labels"
        :displayedData="displayedData"
        :displayedSportIds="displayedSportIds"
        :fullStats="fullStats"
        :useImperialUnits="user.imperial_units"
        :label="
          $t(`statistics.STATISTICS_CHARTS.${chartParams.duration}`) +
          ` (${chartStart} - ${chartEnd})`
        "
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { format } from 'date-fns'
  import { computed, ref, toRefs, watch, onBeforeMount } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import Chart from '@/components/Common/StatsChart/Chart.vue'
  import { STATS_STORE } from '@/store/constants'
  import type { ISport } from '@/types/sports'
  import type {
    IStatisticsChartData,
    TStatisticsDatasetKeys,
    IStatisticsDateParams,
    TStatisticsFromApi,
    IStatisticsParams,
  } from '@/types/statistics'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { dateFormats, formatStats, formatDateLabel } from '@/utils/statistics'

  interface Props {
    sports: ISport[]
    user: IAuthUserProfile
    chartParams: IStatisticsDateParams
    displayedSportIds?: number[]
    fullStats?: boolean
    hideChartIfNoData?: boolean
    isDisabled?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    displayedSportIds: () => [],
    fullStats: false,
    hideChartIfNoData: false,
    isDisabled: false,
  })
  const {
    sports,
    user,
    chartParams,
    displayedSportIds,
    fullStats,
    hideChartIfNoData,
    isDisabled,
  } = toRefs(props)

  const store = useStore()

  const displayedData: Ref<TStatisticsDatasetKeys> = ref('total_distance')
  const statistics: ComputedRef<TStatisticsFromApi> = computed(
    () => store.getters[STATS_STORE.GETTERS.USER_STATS]
  )
  const dateFormat = computed(
    () => dateFormats[chartParams.value.duration].chart
  )
  const chartStart = computed(() =>
    formatDateLabel(
      chartParams.value.start,
      chartParams.value.duration,
      user.value.date_format,
      dateFormat.value
    )
  )
  const chartEnd = computed(() =>
    formatDateLabel(
      chartParams.value.end,
      chartParams.value.duration,
      user.value.date_format,
      dateFormat.value
    )
  )
  const formattedStats: ComputedRef<IStatisticsChartData> = computed(() =>
    formatStats(
      chartParams.value,
      user.value.weekm,
      sports.value,
      displayedSportIds.value,
      statistics.value,
      user.value.imperial_units,
      user.value.date_format
    )
  )
  const datasets = computed(
    () => formattedStats.value.datasets[displayedData.value]
  )
  const labels = computed(() => formattedStats.value.labels)
  const emptyStats = computed(() => Object.keys(statistics.value).length === 0)

  onBeforeMount(() =>
    getStatistics(getApiParams(chartParams.value, user.value))
  )

  function getStatistics(apiParams: IStatisticsParams) {
    store.dispatch(STATS_STORE.ACTIONS.GET_USER_STATS, {
      username: user.value.username,
      filterType: 'by_time',
      params: apiParams,
    })
  }
  function updateDisplayData(event: Event) {
    displayedData.value = (event.target as HTMLInputElement)
      .name as TStatisticsDatasetKeys
  }
  function getApiParams(
    chartParams: IStatisticsDateParams,
    user: IAuthUserProfile
  ): IStatisticsParams {
    return {
      from: format(chartParams.start, 'yyyy-MM-dd'),
      to: format(chartParams.end, 'yyyy-MM-dd'),
      time:
        chartParams.duration === 'week'
          ? `week${user.weekm ? 'm' : ''}`
          : chartParams.duration,
    }
  }

  watch(
    () => chartParams.value,
    async (newParams) => {
      getStatistics(getApiParams(newParams, user.value))
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars';
  .stats-chart {
    width: 100%;
    .chart-radio {
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      padding: $default-padding;

      label {
        font-size: 0.85em;
        font-weight: normal;
        @media screen and (max-width: $small-limit) {
          padding-bottom: $default-padding;
        }
      }
    }
  }
</style>
