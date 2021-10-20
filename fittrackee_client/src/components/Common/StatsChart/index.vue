<template>
  <div class="start-chart">
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
            @click="updateDisplayData"
          />
          {{ $t('workouts.DISTANCE') }}
        </label>
        <label>
          <input
            type="radio"
            name="total_duration"
            :checked="displayedData === 'total_duration'"
            @click="updateDisplayData"
          />
          {{ $t('workouts.DURATION') }}
        </label>
        <label>
          <input
            type="radio"
            name="nb_workouts"
            :checked="displayedData === 'nb_workouts'"
            @click="updateDisplayData"
          />
          {{ $t('workouts.WORKOUT', 2) }}
        </label>
      </div>
      <Chart
        v-if="labels.length > 0"
        :datasets="datasets"
        :labels="labels"
        :displayedData="displayedData"
        :displayedSportIds="displayedSportIds"
        :fullStats="fullStats"
      />
    </div>
  </div>
</template>

<script lang="ts">
  import { format } from 'date-fns'
  import {
    ComputedRef,
    PropType,
    Ref,
    computed,
    defineComponent,
    ref,
    watch,
    onBeforeMount,
  } from 'vue'

  import Chart from '@/components/Common/StatsChart/Chart.vue'
  import { STATS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import {
    IStatisticsChartData,
    TStatisticsDatasetKeys,
    IStatisticsDateParams,
    TStatisticsFromApi,
    IStatisticsParams,
  } from '@/types/statistics'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatStats } from '@/utils/statistics'

  export default defineComponent({
    name: 'UserMonthStats',
    components: {
      Chart,
    },
    props: {
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
      chartParams: {
        type: Object as PropType<IStatisticsDateParams>,
        required: true,
      },
      displayedSportIds: {
        type: Array as PropType<number[]>,
        default: () => [],
      },
      fullStats: {
        type: Boolean,
        default: false,
      },
      hideChartIfNoData: {
        type: Boolean,
        default: false,
      },
    },
    setup(props) {
      const store = useStore()

      let displayedData: Ref<TStatisticsDatasetKeys> = ref('total_distance')
      const statistics: ComputedRef<TStatisticsFromApi> = computed(
        () => store.getters[STATS_STORE.GETTERS.USER_STATS]
      )
      const formattedStats: ComputedRef<IStatisticsChartData> = computed(() =>
        formatStats(
          props.chartParams,
          props.user.weekm,
          props.sports,
          props.displayedSportIds,
          statistics.value
        )
      )

      onBeforeMount(() =>
        getStatistics(getApiParams(props.chartParams, props.user))
      )

      function getStatistics(apiParams: IStatisticsParams) {
        store.dispatch(STATS_STORE.ACTIONS.GET_USER_STATS, {
          username: props.user.username,
          filterType: 'by_time',
          params: apiParams,
        })
      }
      function updateDisplayData(
        event: Event & {
          target: HTMLInputElement & { name: TStatisticsDatasetKeys }
        }
      ) {
        displayedData.value = event.target.name
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
        () => props.chartParams,
        async (newParams) => {
          getStatistics(getApiParams(newParams, props.user))
        }
      )

      return {
        datasets: computed(
          () => formattedStats.value.datasets[displayedData.value]
        ),
        labels: computed(() => formattedStats.value.labels),
        emptyStats: computed(() => Object.keys(statistics.value).length === 0),
        displayedData,
        updateDisplayData,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  .start-chart {
    .chart-radio {
      display: flex;
      justify-content: space-between;
      padding: $default-padding;

      label {
        font-size: 0.85em;
        font-weight: normal;
      }
    }
  }
</style>
