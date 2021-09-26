<template>
  <div class="stat-chart">
    <Chart
      :datasets="datasets"
      :labels="labels"
      :displayedData="displayedData"
    />
  </div>
</template>

<script lang="ts">
  import { ComputedRef, PropType, computed, defineComponent } from 'vue'

  import Chart from '@/components/Common/StatsChart/Chart.vue'
  import { ISport } from '@/types/sports'
  import {
    IStatisticsChartData,
    IStatisticsDateParams,
    TStatisticsDatasetKeys,
    TStatisticsFromApi,
  } from '@/types/statistics'
  import { formatStats } from '@/utils/statistics'

  export default defineComponent({
    name: 'StatsChart',
    components: {
      Chart,
    },
    props: {
      statistics: {
        type: Object as PropType<TStatisticsFromApi>,
        required: true,
      },
      displayedData: {
        type: String as PropType<TStatisticsDatasetKeys>,
        required: true,
      },
      params: {
        type: Object as PropType<IStatisticsDateParams>,
        required: true,
      },
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
      weekStartingMonday: {
        type: Boolean,
        required: true,
      },
    },
    setup(props) {
      const formattedStats: ComputedRef<IStatisticsChartData> = computed(() =>
        formatStats(
          props.params,
          props.weekStartingMonday,
          props.sports,
          [],
          props.statistics
        )
      )
      return {
        datasets: computed(
          () => formattedStats.value.datasets[props.displayedData]
        ),
        labels: computed(() => formattedStats.value.labels),
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  .stat-chart {
    .chart {
      padding: $default-padding;
      max-height: 100%;
    }
  }
</style>
