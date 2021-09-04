<template>
  <div class="chart">
    <BarChart v-bind="barChartProps" />
  </div>
</template>

<script lang="ts">
  import { Chart, ChartData, ChartOptions, registerables } from 'chart.js'
  import { ComputedRef, PropType, computed, defineComponent } from 'vue'
  import { BarChart, useBarChart } from 'vue-chart-3'

  import { IStatisticsChartDataset } from '@/types/statistics'

  Chart.register(...registerables)

  export default defineComponent({
    name: 'Chart',
    components: {
      BarChart,
    },
    props: {
      datasets: {
        type: Object as PropType<IStatisticsChartDataset[]>,
        required: true,
      },
      labels: {
        type: Object as PropType<unknown[]>,
        required: true,
      },
    },
    setup(props) {
      let chartData: ComputedRef<ChartData<'bar'>> = computed(() => ({
        labels: props.labels,
        datasets: props.datasets,
      }))
      const options = computed<ChartOptions<'bar'>>(() => ({
        responsive: true,
        maintainAspectRatio: true,
        layout: {
          padding: 5,
        },
        scales: {
          x: {
            stacked: true,
            grid: {
              display: false,
            },
          },
          y: {
            stacked: true,
            grid: {
              display: false,
            },
          },
        },
        plugins: {
          legend: {
            display: false,
          },
        },
      }))
      const { barChartProps } = useBarChart({
        chartData,
        options,
      })
      return { barChartProps }
    },
  })
</script>
