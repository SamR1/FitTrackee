<template>
  <div id="workout-chart">
    <Card>
      <template #title>{{ $t('workouts.ANALYSIS') }} </template>
      <template #content>
        <div class="split-charts" v-if="displayedDatasets.length > 1">
          <label for="split-chart">
            {{ $t('workouts.DISPLAY_MULTIPLE_CHARTS') }}:
          </label>
          <input
            id="split-chart"
            type="checkbox"
            :checked="splitCharts"
            @click="splitCharts = !splitCharts"
          />
        </div>
        <div class="chart-radio">
          <label>
            <input
              type="radio"
              name="distance"
              :checked="displayDistance"
              :disabled="loading"
              @click="updateDisplayDistance"
            />
            {{ $t('workouts.DISTANCE') }}
          </label>
          <label>
            <input
              type="radio"
              name="duration"
              :disabled="loading"
              :checked="!displayDistance"
              @click="updateDisplayDistance"
            />
            {{ $t('workouts.DURATION') }}
          </label>
        </div>
        <Loader
          v-if="loading"
          class="chart-loader"
          :class="{ multiple: multipleCharts }"
        />
        <div v-for="(data, index) in chartData" :key="data.label">
          <div
            :id="`chart-legend-${data.label}`"
            class="chart-legend"
            :class="{
              loading,
            }"
          />
          <div
            class="line-chart"
            :class="{
              loading,
              multiple: multipleCharts,
            }"
            :ref="`line-chart-${data.label}`"
          >
            <Line
              :id="`line-chart-${data.label}`"
              :ref="
                (element) => {
                  displayedCharts[index] = element as HTMLElement
                }
              "
              :data="data.chartData"
              :options="data.config"
              :plugins="plugins"
              @mouseleave="emitEmptyCoordinates"
              :aria-label="$t('workouts.WORKOUT_CHART')"
            />
          </div>
        </div>
        <div class="chart-info">
          <div class="no-data-cleaning">
            {{ $t('workouts.NO_DATA_CLEANING') }}
          </div>
          <div class="elevation-start" v-if="hasElevation">
            <label>
              <input
                type="checkbox"
                :checked="beginElevationAtZero"
                @click="beginElevationAtZero = !beginElevationAtZero"
              />
              {{ $t('workouts.START_ELEVATION_AT_ZERO') }}
            </label>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import type {
    Chart,
    ChartData,
    ChartOptions,
    LayoutItem,
    TooltipItem,
  } from 'chart.js'
  import type { ComputedRef, Reactive, Ref } from 'vue'
  import { computed, onUnmounted, reactive, ref, toRefs, watch } from 'vue'
  import { Line } from 'vue-chartjs'
  import { useI18n } from 'vue-i18n'
  import { useStore } from 'vuex'

  import Loader from '@/components/Common/Loader.vue'
  import { verticalHoverLine } from '@/components/Workout/WorkoutDetail/WorkoutChart/hoverLine.ts'
  import { htmlLegendPlugin } from '@/components/Workout/WorkoutDetail/WorkoutChart/legend'
  import useApp from '@/composables/useApp'
  import { WORKOUTS_STORE } from '@/store/constants.ts'
  import type { IChartDataset, IHoverPoint } from '@/types/chart.ts'
  import type { TCoordinates } from '@/types/map'
  import type { ISport } from '@/types/sports.ts'
  import type { TUnit } from '@/types/units'
  import type { IAuthUserProfile } from '@/types/user'
  import type { IWorkoutChartData, IWorkoutData } from '@/types/workouts'
  import { formatDuration } from '@/utils/duration.ts'
  import { units } from '@/utils/units'
  import { chartsColors, getCadenceUnit, getDatasets } from '@/utils/workouts'

  interface Props {
    authUser: IAuthUserProfile
    workoutData: IWorkoutData
    sport: ISport | null
  }
  const props = defineProps<Props>()
  const { authUser, sport, workoutData } = toRefs(props)

  const emit = defineEmits(['getCoordinates'])

  const { t } = useI18n()
  const store = useStore()

  const { darkTheme } = useApp()

  const plugins = [htmlLegendPlugin, verticalHoverLine]
  const fromKmUnit = getUnitTo('km')
  const fromMUnit = getUnitTo('m')

  const displayDistance: Ref<boolean> = ref(true)
  const beginElevationAtZero: Ref<boolean> = ref(
    authUser.value.username ? authUser.value.start_elevation_at_zero : false
  )
  const timer: Ref<ReturnType<typeof setTimeout> | undefined> = ref()
  const loading: Ref<boolean> = ref(false)
  const displayedCharts: Ref<HTMLElement[]> = ref([])
  const splitCharts: Ref<boolean> = ref(
    authUser.value.username ? authUser.value.split_workout_charts : false
  )

  const currentDataPoint: Reactive<IHoverPoint> = reactive({
    dataIndex: 0,
    datasetIndex: 0,
    datasetLabel: '',
    x: 0,
    y: 0,
  })

  const hasElevation: ComputedRef<boolean> = computed(
    () => datasets.value && datasets.value.datasets.elevation?.data.length > 0
  )
  const chartLoading: ComputedRef<boolean> = computed(
    () => workoutData.value.chartDataLoading
  )
  const coordinates: ComputedRef<TCoordinates[]> = computed(
    () => datasets.value.coordinates
  )
  const lineColors: ComputedRef<{ color: string }> = computed(() => ({
    color: darkTheme.value
      ? chartsColors.darkMode.line
      : chartsColors.ligthMode.line,
  }))
  const textColors: ComputedRef<{ color: string }> = computed(() => ({
    color: darkTheme.value
      ? chartsColors.darkMode.text
      : chartsColors.ligthMode.text,
  }))
  const datasets: ComputedRef<IWorkoutChartData> = computed(() =>
    getDatasets(
      workoutData.value.chartData,
      t,
      authUser.value.imperial_units,
      darkTheme.value,
      splitCharts.value
    )
  )
  const displayedDatasets = computed(() => {
    const displayedDatasets = [datasets.value.datasets.speed]
    if (datasets.value.datasets.hr.data.length > 0) {
      displayedDatasets.push(datasets.value.datasets.hr)
    }
    if (datasets.value.datasets.cadence.data.length > 0) {
      displayedDatasets.push(datasets.value.datasets.cadence)
    }
    if (datasets.value.datasets.elevation.data.length > 0) {
      displayedDatasets.push(datasets.value.datasets.elevation)
    }
    return displayedDatasets
  })
  const multipleCharts: ComputedRef<boolean> = computed(
    () => displayedDatasets.value.length > 1 && splitCharts.value
  )
  const chartData: ComputedRef<
    {
      label: string
      chartData: ChartData<'line'>
      config: ChartOptions<'line'>
    }[]
  > = computed(() => {
    if (splitCharts.value) {
      return displayedDatasets.value.map((displayedDataset) => {
        return {
          label: displayedDataset.label,
          chartData: {
            labels: displayDistance.value
              ? datasets.value.distance_labels
              : datasets.value.duration_labels,
            datasets: JSON.parse(JSON.stringify([displayedDataset])),
          },
          config: getChartOptions(
            displayedDataset.label,
            beginElevationAtZero.value
          ),
        }
      })
    }
    return [
      {
        label: 'all',
        chartData: {
          labels: displayDistance.value
            ? datasets.value.distance_labels
            : datasets.value.duration_labels,
          datasets: JSON.parse(JSON.stringify(displayedDatasets.value)),
        },
        config: getChartOptions('all', beginElevationAtZero.value),
      },
    ]
  })

  function getChartOptions(
    label: string,
    elevationStartAtZero: boolean
  ): ChartOptions<'line'> {
    return {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      layout: {
        padding: {
          top: 22,
        },
      },
      interaction: {
        intersect: false,
        mode: 'index',
      },
      scales: {
        x: {
          grid: {
            drawOnChartArea: false,
            ...lineColors.value,
          },
          border: {
            ...lineColors.value,
          },
          ticks: {
            count: 10,
            callback: function (value) {
              return displayDistance.value
                ? Number(value).toFixed(2)
                : convertAndFormatDuration(value)
            },
            ...textColors.value,
          },
          type: 'linear',
          bounds: 'data',
          title: {
            display: true,
            text: displayDistance.value
              ? t('workouts.DISTANCE') + ` (${fromKmUnit})`
              : t('workouts.DURATION'),
            ...textColors.value,
          },
        },
        yLeft: {
          beginAtZero: label === 'elevation' ? elevationStartAtZero : false,
          display: true,
          grid: {
            drawOnChartArea: false,
            ...lineColors.value,
          },
          border: {
            ...lineColors.value,
          },
          position: 'left',
          title: {
            display: true,
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            text: (context: any): string[] => {
              const displayedDatasets = getDisplayedDatasets(context, 'yLeft')
              if (displayedDatasets.length === 0) {
                return []
              }
              return displayedDatasets.map(
                (d) => d.label + getUnitLabelForYAxis(d.id)
              )
            },
            ...textColors.value,
          },
          ticks: {
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            display: (context: any): boolean => {
              const displayedDatasets = getDisplayedDatasets(context, 'yLeft')
              return displayedDatasets.length === 1
            },
            ...textColors.value,
          },
          afterFit: function (scale: LayoutItem) {
            scale.width = multipleCharts.value ? 50 : 65
          },
        },
        yRight: {
          display: !multipleCharts.value && displayedDatasets.value.length > 1,
          beginAtZero: hasElevation.value && elevationStartAtZero,
          grid: {
            drawOnChartArea: false,
            ...lineColors.value,
          },
          border: {
            ...lineColors.value,
          },
          position: 'right',
          title: {
            display: true,
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            text: (context: any): string => {
              const displayedDatasets = getDisplayedDatasets(context, 'yRight')
              if (displayedDatasets.length !== 1) {
                return ''
              }
              return (
                displayedDatasets[0].label +
                getUnitLabelForYAxis(displayedDatasets[0].id)
              )
            },
            ...textColors.value,
          },
          ticks: {
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            display(context: any): boolean {
              const displayedDatasets = getDisplayedDatasets(context, 'yRight')
              return displayedDatasets.length === 1
            },
            ...textColors.value,
          },
          afterFit: function (scale: LayoutItem) {
            scale.width = multipleCharts.value ? 50 : 65
          },
        },
      },
      elements: {
        point: {
          pointStyle: 'circle',
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          pointRadius: 0,
        },
      },
      plugins: {
        datalabels: {
          display: false,
        },
        tooltip: {
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          interaction: {
            intersect: false,
            mode: 'index',
          },
          callbacks: {
            label: (context) => getTooltipLabel(context),
            title: (tooltipItems: TooltipItem<any>[]) =>
              getTooltipTitle(tooltipItems),
          },
        },
        legend: {
          display: false,
        },
        htmlLegend: {
          containerID: `chart-legend-${label}`,
          displayElevation: hasElevation.value,
        },
      },
    }
  }
  function updateDisplayDistance() {
    displayDistance.value = !displayDistance.value
  }
  function convertAndFormatDuration(duration: string | number): string {
    const totalSeconds: number =
      typeof duration === 'string'
        ? parseInt(duration.replace(/\s/g, ''))
        : duration
    return formatDuration(totalSeconds, { withHours: true })
  }
  function emitCoordinates(coordinates: TCoordinates) {
    emit('getCoordinates', coordinates)
  }
  function emitEmptyCoordinates() {
    emitCoordinates({ latitude: null, longitude: null })
    handleTooltipOnAllCharts()
  }
  function getUnitTo(unitFrom: TUnit): TUnit {
    return props.authUser.imperial_units
      ? units[unitFrom].defaultTarget
      : unitFrom
  }
  function getUnitLabelForYAxis(datasetId: string | undefined): string {
    switch (datasetId) {
      case 'cadence':
        return ` (${t(`workouts.UNITS.${getCadenceUnit(sport.value?.label)}.UNIT`)})`
      case 'elevation':
        return ` (${fromMUnit})`
      case 'hr':
        return ` (${t('workouts.UNITS.bpm.UNIT')})`
      case 'speed':
        return ` (${fromKmUnit}/h)`
      default:
        return ''
    }
  }
  function getDisplayedDatasets(
    context: any,
    yaxisID: string
  ): IChartDataset[] {
    const chart = context.scale.chart
    return chart.data.datasets.filter(
      (dataset: IChartDataset, index: number) =>
        dataset.yAxisID === yaxisID && !chart.getDatasetMeta(index).hidden
    )
  }
  function getTooltipTitle(tooltipItems: TooltipItem<any>[]) {
    if (tooltipItems.length === 0) {
      return ''
    }
    emitCoordinates(coordinates.value[tooltipItems[0].dataIndex])
    return displayDistance.value
      ? `${t('workouts.DISTANCE')}: ${tooltipItems[0].label} ${fromKmUnit}`
      : `${t('workouts.DURATION')}: ${convertAndFormatDuration(
          tooltipItems[0].label.replace(',', '')
        )}`
  }
  function getTooltipLabel(context: any) {
    currentDataPoint.dataIndex = context.dataIndex
    currentDataPoint.datasetIndex = context.datasetIndex
    currentDataPoint.datasetLabel = `line-chart-${context.dataset.label}`
    currentDataPoint.x = context.parsed.x
    currentDataPoint.y = context.parsed.y

    const label = ` ${context.dataset.label}: ${context.formattedValue}`
    if (context.dataset.id === 'elevation') {
      return label + ` ${fromMUnit}`
    }
    if (context.dataset.id === 'cadence') {
      const unit = getCadenceUnit(sport.value?.label)
      return label + ' ' + t(`workouts.UNITS.${unit}.UNIT`)
    }
    return context.dataset.id === 'hr'
      ? label + ` ${t('workouts.UNITS.bpm.UNIT')}`
      : label + ` ${fromKmUnit}/h`
  }
  function setChartsActivePoints(
    chart: Chart | undefined,
    activePoint?: IHoverPoint
  ) {
    if (!chart || chart.canvas.id === activePoint?.datasetLabel) {
      return
    }
    if (activePoint) {
      chart.setActiveElements([
        {
          datasetIndex: activePoint.datasetIndex,
          index: activePoint.dataIndex,
        },
      ])
      chart.tooltip?.setActiveElements(
        [
          {
            datasetIndex: activePoint.datasetIndex,
            index: activePoint.dataIndex,
          },
        ],
        { x: activePoint.x, y: activePoint.y }
      )
    } else {
      chart.setActiveElements([])
      chart.tooltip?.setActiveElements([], { x: 0, y: 0 })
    }
    chart.update()
  }
  function handleTooltipOnAllCharts(hoveredPoint?: IHoverPoint) {
    if (!splitCharts.value || displayedDatasets.value.length === 1) {
      return
    }
    displayedCharts.value.forEach((element: HTMLElement) => {
      if (element && 'chart' in element) {
        setChartsActivePoints(element.chart as Chart | undefined, hoveredPoint)
      }
    })
  }

  watch(
    () => chartLoading.value,
    (newLoading) => {
      if (newLoading) {
        timer.value = setTimeout(() => {
          store.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA, [])
          loading.value = true
        }, 500)
      } else {
        clearTimeout(timer.value)
        loading.value = false
      }
    },
    { immediate: true }
  )
  watch(
    () => currentDataPoint.dataIndex,
    () => {
      handleTooltipOnAllCharts(currentDataPoint)
    }
  )
  watch(
    () => splitCharts.value,
    () => {
      handleTooltipOnAllCharts()
    }
  )

  onUnmounted(() => {
    if (timer.value) {
      clearTimeout(timer.value)
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #workout-chart {
    ::v-deep(.card) {
      .card-title {
        text-transform: capitalize;
      }
      .card-content {
        display: flex;
        flex-direction: column;
        position: relative;
        .chart-radio {
          width: 100%;
          display: flex;
          justify-content: center;
          label {
            padding: 0 $default-padding;
          }
        }
        .chart-info {
          display: flex;
          justify-content: space-between;
          font-size: 0.85em;
          font-style: italic;
        }
        .chart-legend {
          display: flex;
          justify-content: center;

          &.loading {
            opacity: 0.3;
            pointer-events: none;
          }

          ul {
            display: flex;
            margin-bottom: 0;
            padding: 0;
            flex-wrap: wrap;
            justify-content: space-around;

            li {
              cursor: pointer;
              display: flex;
              font-size: 0.85em;
              padding: 0 $default-padding * 0.5;

              label {
                display: flex;
                font-weight: normal;
                span {
                  border-radius: 5%;
                  border-style: solid;
                  border-width: 1.5px;
                  height: 10px;
                  margin-top: 4px;
                  margin-left: 2px;
                  width: 20px;
                }
              }
            }
          }
        }
        .line-chart {
          height: 400px;

          &.multiple {
            height: 150px;
          }

          &.loading {
            opacity: 0.3;
            pointer-events: none;
          }
        }
        .chart-loader {
          position: absolute;
          margin-top: 200px;
          margin-left: 45%;
          &.multiple {
            margin-top: 50px;
          }
        }
        .split-charts {
          label {
            font-weight: bold;
          }
        }
      }

      @media screen and (max-width: $small-limit) {
        .card-content {
          padding: $default-padding $default-padding * 0.5;
          .chart-info {
            display: flex;
            flex-direction: column-reverse;
            .elevation-start {
              padding: $default-padding $default-padding * 1.5 0;
            }
            .no-data-cleaning {
              padding: 0 $default-padding * 2;
            }
          }
          .split-charts {
            padding-bottom: $default-padding;
            padding-left: $default-padding * 2;
          }
          .line-chart {
            height: 338px;
          }
          .chart-loader {
            margin-left: 40%;
          }
        }
      }
    }
  }
</style>
