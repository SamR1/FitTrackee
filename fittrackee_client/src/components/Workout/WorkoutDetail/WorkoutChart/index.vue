<template>
  <div id="workout-chart">
    <Card>
      <template #title>{{ $t('workouts.ANALYSIS') }} </template>
      <template #content>
        <div class="chart-radio">
          <label>
            <input
              type="radio"
              name="distance"
              :checked="displayDistance"
              @click="updateDisplayDistance"
            />
            {{ $t('workouts.DISTANCE') }}
          </label>
          <label>
            <input
              type="radio"
              name="duration"
              :checked="!displayDistance"
              @click="updateDisplayDistance"
            />
            {{ $t('workouts.DURATION') }}
          </label>
        </div>
        <div id="chart-legend" />
        <div class="line-chart">
          <Line
            :data="chartData"
            :options="options"
            :plugins="plugins"
            @mouseleave="emitEmptyCoordinates"
            :aria-label="$t('workouts.WORKOUT_CHART')"
          />
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
    ChartData,
    ChartOptions,
    LayoutItem,
    TooltipItem,
  } from 'chart.js'
  import { computed, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { Line } from 'vue-chartjs'
  import { useI18n } from 'vue-i18n'

  import { htmlLegendPlugin } from '@/components/Workout/WorkoutDetail/WorkoutChart/legend'
  import useApp from '@/composables/useApp'
  import type { IChartDataset } from '@/types/chart.ts'
  import type { TCoordinates } from '@/types/map'
  import type { ISport } from '@/types/sports.ts'
  import type { TUnit } from '@/types/units'
  import type { IAuthUserProfile } from '@/types/user'
  import type { IWorkoutChartData, IWorkoutData } from '@/types/workouts'
  import { formatDuration } from '@/utils/duration.ts'
  import { units } from '@/utils/units'
  import { chartsColors, getDatasets } from '@/utils/workouts'

  interface Props {
    authUser: IAuthUserProfile
    workoutData: IWorkoutData
    sport: ISport | null
  }
  const props = defineProps<Props>()
  const { authUser, sport, workoutData } = toRefs(props)

  const emit = defineEmits(['getCoordinates'])

  const { t } = useI18n()

  const { darkTheme } = useApp()

  const displayDistance: Ref<boolean> = ref(true)

  const plugins = [htmlLegendPlugin]
  const fromKmUnit = getUnitTo('km')
  const fromMUnit = getUnitTo('m')

  const beginElevationAtZero: Ref<boolean> = ref(
    authUser.value.username ? authUser.value.start_elevation_at_zero : false
  )
  const hasElevation: ComputedRef<boolean> = computed(
    () => datasets.value && datasets.value.datasets.elevation.data.length > 0
  )
  const datasets: ComputedRef<IWorkoutChartData> = computed(() =>
    getDatasets(
      workoutData.value.chartData,
      t,
      authUser.value.imperial_units,
      darkTheme.value
    )
  )
  const chartData: ComputedRef<ChartData<'line'>> = computed(() => {
    const displayedDatasets = [datasets.value.datasets.speed]
    if (datasets.value.datasets.hr.data.length > 0) {
      displayedDatasets.push(datasets.value.datasets.hr)
    }
    if (datasets.value.datasets.cadence.data.length > 0) {
      displayedDatasets.push(datasets.value.datasets.cadence)
    }
    displayedDatasets.push(datasets.value.datasets.elevation)
    return {
      labels: displayDistance.value
        ? datasets.value.distance_labels
        : datasets.value.duration_labels,
      datasets: JSON.parse(JSON.stringify(displayedDatasets)),
    }
  })
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
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const options: ComputedRef<ChartOptions<'line'>> = computed(() => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    layout: {
      padding: {
        top: 22,
      },
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
      yMultiple: {
        display(context: any): boolean {
          const displayedDatasets = getDisplayedDatasets(context)
          return displayedDatasets.length === 1
        },
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
          text: (context: any): string => {
            const displayedDatasets = getDisplayedDatasets(context)
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
          ...textColors.value,
        },
        afterFit: function (scale: LayoutItem) {
          scale.width = 50
        },
      },
      yElevation: {
        beginAtZero: beginElevationAtZero.value,
        display: hasElevation.value,
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
          text: t('workouts.ELEVATION') + ` (${fromMUnit})`,
          ...textColors.value,
        },
        ticks: {
          ...textColors.value,
        },
      },
    },
    elements: {
      point: {
        pointStyle: 'circle',
        pointRadius: 0,
      },
    },
    plugins: {
      datalabels: {
        display: false,
      },
      tooltip: {
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
        containerID: 'chart-legend',
        displayElevation: hasElevation.value,
      },
    },
  }))

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
  }
  function getUnitTo(unitFrom: TUnit): TUnit {
    return props.authUser.imperial_units
      ? units[unitFrom].defaultTarget
      : unitFrom
  }
  function getCadenceUnit(sportLabel: string | undefined) {
    let unit: string
    switch (sportLabel) {
      case 'Cycling (Sport)':
      case 'Cycling (Trekking)':
      case 'Cycling (Transport)':
      case 'Cycling (Virtual)':
      case 'Halfbike':
      case 'Mountain Biking':
      case 'Mountain Biking (Electric)':
        unit = 'rpm'
        break
      case 'Hiking':
      case 'Snowshoes':
      case 'Running':
      case 'Trail':
      case 'Walking':
        unit = 'spm'
        break
      default:
        unit = ''
    }
    if (!unit) {
      return ''
    }
    return t(`workouts.UNITS.${unit}.UNIT`)
  }
  function getUnitLabelForYAxis(datasetId: string | undefined): string {
    switch (datasetId) {
      case 'cadence':
        return ` (${getCadenceUnit(sport.value?.label)})`
      case 'elevation':
        return ` (${fromMUnit})`
      case 'hr':
        return ` (${t('workouts.UNITS.bpm.UNIT')}})`
      case 'speed':
        return ` (${fromKmUnit}/h)`
      default:
        return ''
    }
  }
  function getDisplayedDatasets(context: any): IChartDataset[] {
    const chart = context.scale.chart
    return chart.data.datasets.filter(
      (dataset: IChartDataset, index: number) =>
        dataset.yAxisID !== 'yElevation' && !chart.getDatasetMeta(index).hidden
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
    const label = ` ${context.dataset.label}: ${context.formattedValue}`
    if (context.dataset.yAxisID === 'yElevation') {
      return label + ` ${fromMUnit}`
    }
    if (context.dataset.id === 'cadence') {
      const unit = getCadenceUnit(sport.value?.label)
      return label + ' ' + unit
    }
    return context.dataset.id === 'hr'
      ? label + ` ${t('workouts.UNITS.bpm.UNIT')}`
      : label + ` ${fromKmUnit}/h`
  }
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
        #chart-legend {
          display: flex;
          justify-content: center;

          ul {
            display: flex;
            margin-bottom: 0;
            padding: 0;

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
          min-height: 400px;
        }
      }

      @media screen and (max-width: $small-limit) {
        .card-content {
          padding: $default-padding 0;
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
          .line-chart {
            min-height: 338px;
          }
        }
      }
    }
  }
</style>
