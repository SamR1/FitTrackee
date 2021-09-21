<template>
  <div class="chart">
    <BarChart v-bind="barChartProps" class="bar-chart" />
  </div>
</template>

<script lang="ts">
  import {
    Chart,
    ChartData,
    ChartOptions,
    LayoutItem,
    registerables,
  } from 'chart.js'
  import ChartDataLabels from 'chartjs-plugin-datalabels'
  import { ComputedRef, PropType, computed, defineComponent } from 'vue'
  import { BarChart, useBarChart } from 'vue-chart-3'
  import { useI18n } from 'vue-i18n'

  import { IStatisticsChartDataset, TDatasetKeys } from '@/types/statistics'
  import { formatTooltipValue } from '@/utils/tooltip'

  Chart.register(...registerables)
  Chart.register(ChartDataLabels)

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
      const { t } = useI18n()
      // eslint-disable-next-line
      function getNumber(value: any): number {
        return isNaN(value) ? 0 : +value
      }
      // eslint-disable-next-line
      function getSum(total: any, value: any): number {
        return getNumber(total) + getNumber(value)
      }
      let chartData: ComputedRef<ChartData<'bar'>> = computed(() => ({
        labels: props.labels,
        // workaround to avoid dataset modification
        datasets: JSON.parse(JSON.stringify(props.datasets)),
      }))
      const options = computed<ChartOptions<'bar'>>(() => ({
        responsive: true,
        maintainAspectRatio: true,
        animation: false,
        layout: {
          padding: {
            top: 22,
          },
        },
        scales: {
          x: {
            stacked: true,
            grid: {
              drawOnChartArea: false,
            },
          },
          y: {
            stacked: true,
            grid: {
              drawOnChartArea: false,
            },
            ticks: {
              maxTicksLimit: 6,
              callback: function (value) {
                return formatTooltipValue(props.displayedData, +value, false)
              },
            },
            afterFit: function (scale: LayoutItem) {
              scale.width = 60
            },
          },
        },
        plugins: {
          datalabels: {
            anchor: 'end',
            align: 'end',
            formatter: function (value, context) {
              // eslint-disable-next-line @typescript-eslint/ban-ts-comment
              // @ts-ignore
              const total: number = context.chart.data.datasets
                .map((d) => d.data[context.dataIndex])
                .reduce((total, value) => getSum(total, value), 0)
              return context.datasetIndex === 5 && total > 0
                ? formatTooltipValue(props.displayedData, total, false)
                : null
            },
          },
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
                let label = t(`sports.${context.dataset.label}.LABEL`) || ''
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
                return (
                  `${t('statistics.TOTAL')}: ` +
                  formatTooltipValue(props.displayedData, sum)
                )
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
