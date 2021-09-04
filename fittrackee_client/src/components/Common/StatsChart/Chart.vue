<template>
  <div class="chart">
    <BarChart v-bind="barChartProps" />
  </div>
</template>

<script lang="ts">
  import { Chart, ChartData, ChartOptions, registerables } from 'chart.js'
  import { ComputedRef, PropType, computed, defineComponent } from 'vue'
  import { BarChart, useBarChart } from 'vue-chart-3'

  import { IStatisticsChartDataset, TDatasetKeys } from '@/types/statistics'
  import { formatTooltipValue } from '@/utils/tooltip'

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
      displayedData: {
        type: String as PropType<TDatasetKeys>,
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
          tooltip: {
            interaction: {
              intersect: true,
              mode: 'index',
            },
            filter: function (tooltipItem) {
              return tooltipItem.formattedValue !== '0'
            },
            callbacks: {
              label: function (context) {
                let label = context.dataset.label || ''
                if (label) {
                  label += ': '
                }
                if (context.parsed.y !== null) {
                  label += formatTooltipValue(
                    props.displayedData,
                    context.parsed.y
                  )
                }
                return label
              },
              footer: function (tooltipItems) {
                let sum = 0
                tooltipItems.map((tooltipItem) => {
                  sum += tooltipItem.parsed.y
                })
                return 'Total: ' + formatTooltipValue(props.displayedData, sum)
              },
            },
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
