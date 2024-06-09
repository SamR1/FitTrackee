<template>
  <div class="bar-chart" :class="{ minimal: !fullStats }">
    <Bar :data="chartData" :options="options" :aria-label="label" />
  </div>
</template>

<script setup lang="ts">
  import type { ChartOptions, LayoutItem } from 'chart.js'
  import { computed, type ComputedRef, toRefs } from 'vue'
  import { Bar } from 'vue-chartjs'
  import { useI18n } from 'vue-i18n'
  import { useStore } from 'vuex'

  import { ROOT_STORE } from '@/store/constants'
  import type { IChartDataset } from '@/types/chart'
  import type { TStatisticsDatasetKeys } from '@/types/statistics'
  import { getDarkTheme } from '@/utils'
  import { formatTooltipValue } from '@/utils/tooltip'
  import { chartsColors } from '@/utils/workouts'

  interface Props {
    datasets: IChartDataset[]
    labels: unknown[]
    displayedData: TStatisticsDatasetKeys
    displayedSportIds: number[]
    fullStats: boolean
    useImperialUnits: boolean
    label: string
  }
  const props = defineProps<Props>()
  const {
    datasets,
    labels,
    displayedData,
    displayedSportIds,
    fullStats,
    useImperialUnits,
  } = toRefs(props)

  const store = useStore()
  const { t } = useI18n()

  const darkMode: ComputedRef<boolean | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DARK_MODE]
  )
  const darkTheme: ComputedRef<boolean> = computed(() =>
    getDarkTheme(darkMode.value)
  )
  const lineColors = computed(() => ({
    color: darkTheme.value
      ? chartsColors.darkMode.line
      : chartsColors.ligthMode.line,
  }))
  const textColors = computed(() => ({
    color: darkTheme.value
      ? chartsColors.darkMode.text
      : chartsColors.ligthMode.text,
  }))
  const isLineChart = computed(
    () =>
      displayedData.value !== 'average_workouts' &&
      displayedData.value.startsWith('average')
  )

  const chartData = computed(() => ({
    labels: labels.value,
    // workaround to avoid dataset modification
    datasets: JSON.parse(JSON.stringify(datasets.value)),
  }))
  const options = computed<ChartOptions<'bar'>>(() => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    layout: {
      padding: {
        top: fullStats.value ? 40 : 22,
      },
    },
    scales: {
      x: {
        stacked: true,
        grid: {
          drawOnChartArea: false,
          ...lineColors.value,
        },
        border: {
          ...lineColors.value,
        },
        ticks: {
          ...textColors.value,
        },
      },
      y: {
        stacked: !displayedData.value.startsWith('average'),
        grid: {
          drawOnChartArea: false,
          ...lineColors.value,
        },
        border: {
          ...lineColors.value,
        },
        ticks: {
          maxTicksLimit: 6,
          callback: function (value) {
            return formatTooltipValue(
              displayedData.value,
              +value,
              useImperialUnits.value,
              false,
              getUnit(displayedData.value)
            )
          },
          ...textColors.value,
        },
        afterFit: function (scale: LayoutItem) {
          scale.width = fullStats.value ? 90 : 60
        },
      },
    },
    plugins: {
      datalabels: {
        anchor: 'end',
        align: 'end',
        color: function (context) {
          return isLineChart.value && context.dataset.backgroundColor
            ? // eslint-disable-next-line @typescript-eslint/ban-ts-comment
              // @ts-ignore
              context.dataset.backgroundColor[0]
            : textColors.value.color
        },
        rotation: function (context) {
          return fullStats.value && context.chart.chartArea.width < 580
            ? 310
            : 0
        },
        display: function (context) {
          return fullStats.value && context.chart.chartArea.width < 300
            ? false
            : isLineChart.value
              ? displayedSportIds.value.length == 1
                ? 'auto'
                : false
              : true
        },
        formatter: function (value, context) {
          if (displayedData.value.startsWith('average')) {
            return formatTooltipValue(
              displayedData.value,
              value,
              useImperialUnits.value,
              false
            )
          } else {
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            const total: number = context.chart.data.datasets
              .map((d) => d.data[context.dataIndex])
              .reduce((total, value) => getSum(total, value), 0)
            return context.datasetIndex ===
              displayedSportIds.value.length - 1 && total > 0
              ? formatTooltipValue(
                  displayedData.value,
                  total,
                  useImperialUnits.value,
                  false,
                  getUnit(displayedData.value)
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
          position: isLineChart.value ? 'nearest' : 'average',
        },
        filter: function (tooltipItem) {
          return tooltipItem.formattedValue !== '0'
        },
        callbacks: {
          label: function (context) {
            let label =
              displayedData.value === 'average_workouts'
                ? t('workouts.WORKOUT', 0)
                : t(`sports.${context.dataset.label}.LABEL`) || ''
            if (label) {
              label += ': '
            }
            if (context.parsed.y !== null) {
              label += formatTooltipValue(
                displayedData.value,
                context.parsed.y,
                useImperialUnits.value,
                true,
                getUnit(displayedData.value)
              )
            }
            return label
          },
          footer: function (tooltipItems) {
            if (displayedData.value.startsWith('average')) {
              return ''
            }
            let sum = 0
            tooltipItems.map((tooltipItem) => {
              sum += tooltipItem.parsed.y
            })
            return (
              `${t('common.TOTAL')}: ` +
              formatTooltipValue(
                displayedData.value,
                sum,
                useImperialUnits.value,
                true,
                getUnit(displayedData.value)
              )
            )
          },
        },
      },
    },
  }))

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function getNumber(value: any): number {
    return isNaN(value) ? 0 : +value
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function getSum(total: any, value: any): number {
    return getNumber(total) + getNumber(value)
  }
  function getUnit(displayedData: string) {
    return ['total_ascent', 'total_descent'].includes(displayedData)
      ? 'm'
      : 'km'
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .bar-chart {
    position: relative;
    min-height: 400px;
    width: 100%;
    &.minimal {
      min-height: 300px;
    }

    @media screen and (max-width: $small-limit) {
      min-height: 268px;
      &.minimal {
        min-height: 290px;
      }
    }

    @media screen and (max-width: 420px) {
      width: calc(100vw - 95px);
    }
  }
</style>
