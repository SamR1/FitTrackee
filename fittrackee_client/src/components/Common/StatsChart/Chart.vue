<template>
  <div class="chart">
    <BarChart v-bind="barChartProps" class="bar-chart" />
  </div>
</template>

<script lang="ts">
  import { ChartData, ChartOptions, LayoutItem } from 'chart.js'
  import { ComputedRef, PropType, computed, defineComponent } from 'vue'
  import { BarChart, useBarChart } from 'vue-chart-3'
  import { useI18n } from 'vue-i18n'

  import { IChartDataset } from '@/types/chart'
  import { TStatisticsDatasetKeys } from '@/types/statistics'
  import { formatTooltipValue } from '@/utils/tooltip'

  export default defineComponent({
    name: 'Chart',
    components: {
      BarChart,
    },
    props: {
      datasets: {
        type: Object as PropType<IChartDataset[]>,
        required: true,
      },
      labels: {
        type: Object as PropType<unknown[]>,
        required: true,
      },
      displayedData: {
        type: String as PropType<TStatisticsDatasetKeys>,
        required: true,
      },
      displayedSportIds: {
        type: Array as PropType<number[]>,
        required: true,
      },
      fullStats: {
        type: Boolean,
        required: true,
      },
      useImperialUnits: {
        type: Boolean,
        required: true,
      },
    },
    setup(props) {
      const { t } = useI18n()
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      function getNumber(value: any): number {
        return isNaN(value) ? 0 : +value
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
            top: props.fullStats ? 40 : 22,
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
            stacked: props.displayedData !== 'average_speed',
            grid: {
              drawOnChartArea: false,
            },
            ticks: {
              maxTicksLimit: 6,
              callback: function (value) {
                return formatTooltipValue(
                  props.displayedData,
                  +value,
                  props.useImperialUnits,
                  false
                )
              },
            },
            afterFit: function (scale: LayoutItem) {
              scale.width = props.fullStats ? 75 : 60
            },
          },
        },
        plugins: {
          datalabels: {
            anchor: 'end',
            align: 'end',
            color: function (context) {
              return props.displayedData === 'average_speed' &&
                context.dataset.backgroundColor
                ? // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                  // @ts-ignore
                  context.dataset.backgroundColor[0]
                : '#666666'
            },
            rotation: function (context) {
              return props.fullStats && context.chart.chartArea.width < 580
                ? 310
                : 0
            },
            display: function (context) {
              return props.fullStats && context.chart.chartArea.width < 300
                ? false
                : props.displayedData === 'average_speed'
                ? props.displayedSportIds.length == 1
                  ? 'auto'
                  : false
                : true
            },
            formatter: function (value, context) {
              if (props.displayedData === 'average_speed') {
                return formatTooltipValue(
                  props.displayedData,
                  value,
                  props.useImperialUnits,
                  false
                )
              } else {
                // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                // @ts-ignore
                const total: number = context.chart.data.datasets
                  .map((d) => d.data[context.dataIndex])
                  .reduce((total, value) => getSum(total, value), 0)
                return context.datasetIndex ===
                  props.displayedSportIds.length - 1 && total > 0
                  ? formatTooltipValue(
                      props.displayedData,
                      total,
                      props.useImperialUnits,
                      false
                    )
                  : null
              }
            },
          },
          legend: {
            display: false,
          },
          tooltip: {
            interaction: {
              intersect: true,
              mode: 'index',
              position:
                props.displayedData === 'average_speed' ? 'nearest' : 'average',
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
                    context.parsed.y,
                    props.useImperialUnits
                  )
                }
                return label
              },
              footer: function (tooltipItems) {
                if (props.displayedData === 'average_speed') {
                  return ''
                }
                let sum = 0
                tooltipItems.map((tooltipItem) => {
                  sum += tooltipItem.parsed.y
                })
                return (
                  `${t('common.TOTAL')}: ` +
                  formatTooltipValue(
                    props.displayedData,
                    sum,
                    props.useImperialUnits
                  )
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
