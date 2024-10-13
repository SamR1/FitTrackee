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
            name="value_type"
            :value="`${statsType}_distance`"
            :checked="displayedData === `${statsType}_distance`"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.DISTANCE') }}
        </label>
        <label>
          <input
            type="radio"
            name="value_type"
            :value="`${statsType}_duration`"
            :checked="displayedData === `${statsType}_duration`"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.DURATION') }}
        </label>
        <label>
          <input
            type="radio"
            name="value_type"
            :value="`${statsType}_workouts`"
            :checked="displayedData === `${statsType}_workouts`"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.WORKOUT', 2) }}
        </label>
        <label v-if="fullStats && statsType === 'average'">
          <input
            type="radio"
            name="value_type"
            value="average_speed"
            :checked="displayedData === 'average_speed'"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.SPEED') }}
        </label>
        <label v-if="fullStats">
          <input
            type="radio"
            name="value_type"
            :value="`${statsType}_ascent`"
            :checked="displayedData === `${statsType}_ascent`"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.ASCENT') }}
        </label>
        <label v-if="fullStats">
          <input
            type="radio"
            name="value_type"
            :value="`${statsType}_descent`"
            :checked="displayedData === `${statsType}_descent`"
            :disabled="isDisabled"
            @click="updateDisplayData"
          />
          {{ $t('workouts.DESCENT') }}
        </label>
      </div>
      <Chart
        v-if="labels.length > 0 || workoutsAverageDataset.labels.length > 0"
        :datasets="
          displayedData === 'average_workouts'
            ? workoutsAverageDataset.datasets.workouts_average
            : datasets
        "
        :labels="
          displayedData === 'average_workouts'
            ? workoutsAverageDataset.labels
            : labels
        "
        :displayedData="displayedData"
        :displayedSportIds="displayedSportIds"
        :fullStats="fullStats"
        :useImperialUnits="user.imperial_units"
        :label="
          $t(`statistics.STATISTICS_CHARTS.${chartParams.duration}`) +
          ` (${chartStart} - ${chartEnd})`
        "
      />
      <div class="workouts-average">
        <div
          v-if="displayedData === 'average_workouts' && selectedTimeFrame"
          class="info-box"
        >
          <i class="fa fa-info-circle" aria-hidden="true" />
          {{ $t('statistics.DATES') }}: {{ chartStart }} - {{ chartEnd }},
          {{ $t('statistics.WORKOUTS_AVERAGE') }}:
          {{ workoutsAverageDataset.workoutsAverage }}/{{
            $t(`statistics.TIME_FRAMES.${selectedTimeFrame}`)
          }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { format } from 'date-fns'
  import { computed, ref, toRefs, watch, onBeforeMount } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Chart from '@/components/Common/StatsChart/Chart.vue'
  import { STATS_STORE } from '@/store/constants'
  import type { IChartDataset } from '@/types/chart'
  import type { ISport } from '@/types/sports'
  import type {
    IStatisticsChartData,
    TStatisticsDatasetKeys,
    IStatisticsDateParams,
    TStatisticsFromApi,
    IStatisticsParams,
    TStatisticsType,
    TStatisticsTimeFrame,
  } from '@/types/statistics'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import {
    dateFormats,
    formatStats,
    formatDateLabel,
    getWorkoutsAverageDatasets,
  } from '@/utils/statistics'

  interface Props {
    sports: ISport[]
    user: IAuthUserProfile
    chartParams: IStatisticsDateParams
    displayedSportIds?: number[]
    fullStats?: boolean
    hideChartIfNoData?: boolean
    isDisabled?: boolean
    selectedTimeFrame?: TStatisticsTimeFrame | null
  }
  const props = withDefaults(defineProps<Props>(), {
    displayedSportIds: () => [],
    fullStats: false,
    hideChartIfNoData: false,
    isDisabled: false,
    selectedTimeFrame: null,
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
  const { t } = useI18n()

  const displayedData: Ref<TStatisticsDatasetKeys> = ref('total_distance')

  const statistics: ComputedRef<TStatisticsFromApi> = computed(
    () => store.getters[STATS_STORE.GETTERS.USER_STATS]
  )
  const chartDateFormat: ComputedRef<string> = computed(
    () => dateFormats[chartParams.value.duration].chart
  )
  const chartStart: ComputedRef<string> = computed(() =>
    formatDateLabel(
      chartParams.value.start,
      chartParams.value.duration,
      user.value.date_format,
      chartDateFormat.value
    )
  )
  const chartEnd: ComputedRef<string> = computed(() =>
    formatDateLabel(
      chartParams.value.end,
      chartParams.value.duration,
      user.value.date_format,
      chartDateFormat.value
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
  const datasets: ComputedRef<IChartDataset[]> = computed(
    () => formattedStats.value.datasets[displayedData.value]
  )
  const labels: ComputedRef<unknown[]> = computed(
    () => formattedStats.value.labels
  )
  const emptyStats: ComputedRef<boolean> = computed(
    () => Object.keys(statistics.value).length === 0
  )
  const statsType: ComputedRef<TStatisticsType> = computed(
    () => chartParams.value.statsType
  )
  const workoutsAverageDataset = computed(() =>
    getWorkoutsAverageDatasets(formattedStats.value.datasets.total_workouts, t)
  )

  function getStatistics(apiParams: IStatisticsParams) {
    store.dispatch(STATS_STORE.ACTIONS.GET_USER_STATS, {
      username: user.value.username,
      params: apiParams,
    })
  }
  function updateDisplayData(event: Event) {
    displayedData.value = (event.target as HTMLInputElement)
      .value as TStatisticsDatasetKeys
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
      type: statsType.value,
    }
  }

  watch(
    () => chartParams.value,
    async (newParams) => {
      getStatistics(getApiParams(newParams, user.value))
    }
  )
  watch(
    () => statsType.value,
    async (newStatsType) => {
      displayedData.value =
        newStatsType === 'total' && displayedData.value === 'average_speed'
          ? 'total_distance'
          : (`${statsType.value}_${displayedData.value.split('_')[1]}` as TStatisticsDatasetKeys)
    }
  )

  onBeforeMount(() =>
    getStatistics(getApiParams(chartParams.value, user.value))
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

    .workouts-average {
      display: flex;
      margin: $default-padding 0 0 $default-padding * 2.5;
      min-height: 20px;

      .fa-info-circle {
        padding-right: $default-padding * 0.5;
      }

      @media screen and (max-width: $small-limit) {
        .fa-info-circle {
          padding-right: $default-padding * 0.2;
        }
        .info-box {
          padding: $default-padding * 0.5 $default-padding;
        }
      }
    }
  }
</style>
