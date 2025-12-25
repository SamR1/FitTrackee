<template>
  <div id="workout-chart">
    <Card>
      <template #title>{{ $t('workouts.ANALYSIS') }} </template>
      <template #content>
        <div class="chart-display">
          <div class="chart-options">
            <div class="split-charts" v-if="displayedDatasets.length > 1">
              <label for="split-chart">
                {{ $t('workouts.DISPLAY_MULTIPLE_CHARTS') }}:
              </label>
              <input
                id="split-chart"
                type="checkbox"
                :checked="splitCharts"
                :disabled="workoutData.refreshLoading"
                @click="splitCharts = !splitCharts"
              />
            </div>
            <div
              class="display-speed"
              v-if="hasPace && displaySpeedWithPacePreferences"
            >
              <label for="display-speed">
                {{ $t('workouts.SPEED_INSTEAD_OF_PACE') }}:
              </label>
              <input
                id="display-speed"
                type="checkbox"
                :checked="displaySpeed"
                :disabled="workoutData.refreshLoading"
                @click="displaySpeed = !displaySpeed"
              />
            </div>
          </div>
        </div>
        <div class="chart-radio">
          <label>
            <input
              type="radio"
              name="distance"
              :checked="displayDistance"
              :disabled="loading || workoutData.refreshLoading"
              @click="updateDisplayDistance"
            />
            {{ $t('workouts.DISTANCE') }}
          </label>
          <label>
            <input
              type="radio"
              name="duration"
              :disabled="loading || workoutData.refreshLoading"
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
        <div v-for="(data, index) in chartData" :key="data.id">
          <div
            :id="`chart-legend-${data.id}`"
            class="chart-legend"
            :class="{ loading }"
          />
          <div
            class="line-chart"
            :class="{
              loading,
              multiple: multipleCharts,
            }"
            :ref="`line-chart-${data.id}`"
          >
            <Line
              :id="`line-chart-${data.id}`"
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
          <div class="chart-info" v-if="data.id === 'pace' && splitCharts">
            <div class="data-info">
              {{ $t('workouts.EXTREME_VALUES_FOR_PACE_ARE_NOT_DISPLAYED') }}
            </div>
          </div>
        </div>
        <div class="chart-info">
          <div class="data-info">
            <span v-if="elevationsSource !== 'none'">
              {{ $t('workouts.MISSING_ELEVATIONS_PROCESSING.LABEL') }}
              {{
                $t(`workouts.MISSING_ELEVATIONS_PROCESSING.${elevationsSource}`)
              }}
            </span>
            <span v-else-if="isWorkoutOwner">
              {{ $t('workouts.NO_DATA_CLEANING') }}
            </span>
          </div>
          <div class="elevation-start" v-if="hasElevation">
            <label>
              <input
                type="checkbox"
                :checked="beginElevationAtZero"
                :disabled="workoutData.refreshLoading"
                @click="beginElevationAtZero = !beginElevationAtZero"
              />
              {{ $t('workouts.START_ELEVATION_AT_ZERO') }}
            </label>
          </div>
        </div>
        <div class="chart-info" v-if="!splitCharts && paceDisplayed">
          <div class="data-info">
            {{ $t('workouts.EXTREME_VALUES_FOR_PACE_ARE_NOT_DISPLAYED') }}
            <template v-if="!onlyPaceDisplayed">
              {{ $t('workouts.VERTICAL_AXIS_FOR_PACE_IS_REVERSED') }}
            </template>
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
    Plugin,
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
  import type {
    IAuthUserProfile,
    TMissingElevationsProcessing,
  } from '@/types/user'
  import type { IWorkoutChartData, IWorkoutData } from '@/types/workouts'
  import { formatDuration } from '@/utils/duration.ts'
  import { units } from '@/utils/units'
  import { chartsColors, getCadenceUnit, getDatasets } from '@/utils/workouts'

  interface Props {
    authUser: IAuthUserProfile
    workoutData: IWorkoutData
    sport: ISport | null
    isWorkoutOwner: boolean
  }
  const props = defineProps<Props>()
  const { authUser, sport, workoutData } = toRefs(props)

  const emit = defineEmits(['getCoordinates'])

  const { t } = useI18n()
  const store = useStore()

  const { darkTheme } = useApp()
  const { displayOptions } = useApp()

  const plugins = [htmlLegendPlugin, verticalHoverLine] as Plugin<'line'>[]
  const fromKmUnit = getUnitTo('km')
  const fromMUnit = getUnitTo('m')

  const timer: Ref<ReturnType<typeof setTimeout> | undefined> = ref()
  const loading: Ref<boolean> = ref(false)
  const displayDistance: Ref<boolean> = ref(true)
  const beginElevationAtZero: Ref<boolean> = ref(
    authUser.value.username ? authUser.value.start_elevation_at_zero : false
  )
  const displayedCharts: Ref<HTMLElement[]> = ref([])
  const splitCharts: Ref<boolean> = ref(
    authUser.value.username ? authUser.value.split_workout_charts : false
  )
  const displaySpeedWithPacePreferences: Ref<boolean> = ref(
    authUser.value.username ? authUser.value.display_speed_with_pace : false
  )
  const paceDisplayed = ref(false)
  const onlyPaceDisplayed = ref(false)
  const displaySpeed = ref(false)

  const currentDataPoint: Reactive<IHoverPoint> = reactive({
    dataIndex: 0,
    datasetIndex: 0,
    datasetLabel: '',
    x: 0,
    y: 0,
  })

  const elevationsSource: ComputedRef<TMissingElevationsProcessing> = computed(
    () =>
      workoutData.value.workout.missing_elevations_processing
        ? workoutData.value.workout.missing_elevations_processing
        : 'none'
  )
  const chartLoading: ComputedRef<boolean> = computed(
    () => workoutData.value.chartDataLoading
  )
  const lineColors: ComputedRef<{ color: string }> = computed(() => ({
    color: darkTheme.value
      ? chartsColors.darkMode.line
      : chartsColors.lightMode.line,
  }))
  const textColors: ComputedRef<{ color: string }> = computed(() => ({
    color: darkTheme.value
      ? chartsColors.darkMode.text
      : chartsColors.lightMode.text,
  }))

  const datasets: ComputedRef<IWorkoutChartData> = computed(() =>
    getDatasets(
      workoutData.value.chartData,
      t,
      displayOptions.value.useImperialUnits,
      darkTheme.value,
      splitCharts.value
    )
  )
  const coordinates: ComputedRef<TCoordinates[]> = computed(
    () => datasets.value.coordinates
  )
  const hasElevation: ComputedRef<boolean> = computed(
    () => datasets.value && datasets.value.datasets.elevation?.data.length > 0
  )
  const hasPace: ComputedRef<boolean> = computed(
    () => datasets.value && datasets.value.datasets.pace?.data.length > 0
  )
  const displayedDatasets = computed(() => {
    const displayedDatasets = [
      hasPace.value && !displaySpeed.value
        ? datasets.value.datasets.pace
        : datasets.value.datasets.speed,
    ]
    if (datasets.value.datasets.hr.data.length > 0) {
      displayedDatasets.push(datasets.value.datasets.hr)
    }
    if (datasets.value.datasets.cadence.data.length > 0) {
      displayedDatasets.push(datasets.value.datasets.cadence)
    }
    if (datasets.value.datasets.power.data.length > 0) {
      displayedDatasets.push(datasets.value.datasets.power)
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
      id: string
      label: string
      chartData: ChartData<'line'>
      config: ChartOptions<'line'>
    }[]
  > = computed(() => {
    if (splitCharts.value) {
      return displayedDatasets.value.map((displayedDataset) => {
        return {
          id: displayedDataset.id as string,
          label: displayedDataset.label,
          chartData: {
            labels: displayDistance.value
              ? datasets.value.distance_labels
              : datasets.value.duration_labels,
            datasets: JSON.parse(JSON.stringify([displayedDataset])),
          },
          config: getChartOptions(
            displayedDataset.id as string,
            beginElevationAtZero.value
          ),
        }
      })
    }
    return [
      {
        id: 'all',
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
    id: string,
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
          beginAtZero: id === 'elevation' ? elevationStartAtZero : false,
          // @ts-expect-error  @typescript-eslint/ban-ts-comment
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          max: (context: any): number | undefined => {
            if (context.type !== 'scale') {
              return undefined
            }
            // When the pace is displayed, extreme values (i.e. greater than
            // 1 hour) are not shown.
            return isPaceOnlyDisplayed(context) ? 3600 : undefined
          },
          display: true,
          grid: {
            drawOnChartArea: false,
            ...lineColors.value,
          },
          border: {
            ...lineColors.value,
          },
          position: 'left',
          // @ts-expect-error  @typescript-eslint/ban-ts-comment
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          reverse: (context: any): boolean => {
            return isPaceOnlyDisplayed(context)
          },
          title: {
            display: true,
            // @ts-expect-error  @typescript-eslint/ban-ts-comment
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
            // @ts-expect-error  @typescript-eslint/ban-ts-comment
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            display: (context: any): boolean => {
              const displayedDatasetIds = getDisplayedDatasets(
                context,
                'yLeft'
              ).map(({ id }) => id)
              paceDisplayed.value = displayedDatasetIds.includes('pace')
              onlyPaceDisplayed.value =
                displayedDatasetIds.length === 1 &&
                displayedDatasetIds[0] === 'pace'
              return displayedDatasetIds.length === 1
            },
            callback: function (value) {
              return id === 'pace' || onlyPaceDisplayed.value
                ? formatDuration(+value, {
                    notPadded: true,
                  })
                : value
            },
            ...textColors.value,
          },
          afterFit: function (scale: LayoutItem) {
            scale.width = 67
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
            // @ts-expect-error  @typescript-eslint/ban-ts-comment
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
            // @ts-expect-error  @typescript-eslint/ban-ts-comment
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            title: (tooltipItems: TooltipItem<any>[]) =>
              getTooltipTitle(tooltipItems),
          },
        },
        legend: {
          display: false,
        },
        htmlLegend: {
          containerID: `chart-legend-${id}`,
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
    return displayOptions.value.useImperialUnits
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
      case 'power':
        return ` (W)`
      case 'pace':
        return ` (min/${fromKmUnit})`
      default:
        return ''
    }
  }
  function getDisplayedDatasets(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    context: any,
    yaxisID: string
  ): IChartDataset[] {
    const chart = context.scale.chart
    return chart.data.datasets.filter(
      (dataset: IChartDataset, index: number) =>
        dataset.yAxisID === yaxisID && !chart.getDatasetMeta(index).hidden
    )
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function isPaceOnlyDisplayed(context: any) {
    const displayedDatasets = getDisplayedDatasets(context, 'yLeft')
    return (
      context.chart.canvas.id === 'line-chart-pace' ||
      (displayedDatasets.length === 1 && displayedDatasets[0].id === 'pace')
    )
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function getTooltipLabel(context: any) {
    currentDataPoint.dataIndex = context.dataIndex
    currentDataPoint.datasetIndex = context.datasetIndex
    currentDataPoint.datasetLabel = `line-chart-${context.dataset.id}`
    currentDataPoint.x = context.parsed.x
    currentDataPoint.y = context.parsed.y

    if (context.dataset.id === 'pace') {
      const formattedValue = formatDuration(context.raw, {
        notPadded: true,
      })
      const unit = displayOptions.value.useImperialUnits ? 'min/mi' : 'min/km'
      return ` ${context.dataset.label}: ${formattedValue} ${unit}`
    }
    const label = ` ${context.dataset.label}: ${context.formattedValue}`
    if (context.dataset.id === 'elevation') {
      return label + ` ${fromMUnit}`
    }
    if (context.dataset.id === 'cadence') {
      const unit = getCadenceUnit(sport.value?.label)
      return label + ' ' + t(`workouts.UNITS.${unit}.UNIT`)
    }
    if (context.dataset.id === 'power') {
      return `${label} W`
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
    try {
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
    } catch {
      return
    }
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
        .chart-display {
          display: flex;
          gap: $default-margin;
          margin-bottom: $default-margin * 0.5;
          font-weight: bold;

          .chart-options {
            display: flex;
            gap: $default-margin;
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
            .data-info {
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

      @media screen and (max-width: $x-small-limit) {
        .chart-display {
          .chart-options {
            flex-direction: column;
            gap: 0 !important;
            margin-bottom: $default-margin;
            .split-charts,
            .display-speed {
              margin: 0;
              padding: 0;
            }
          }
        }
      }
    }
  }
</style>
