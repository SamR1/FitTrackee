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
  import type { ChartData, ChartOptions } from 'chart.js'
  import { computed, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { Line } from 'vue-chartjs'
  import { useI18n } from 'vue-i18n'

  import { htmlLegendPlugin } from '@/components/Workout/WorkoutDetail/WorkoutChart/legend'
  import useApp from '@/composables/useApp'
  import type { TCoordinates } from '@/types/map'
  import type { TUnit } from '@/types/units'
  import type { IAuthUserProfile } from '@/types/user'
  import type { IWorkoutChartData, IWorkoutData } from '@/types/workouts'
  import { units } from '@/utils/units'
  import { chartsColors, getDatasets } from '@/utils/workouts'

  interface Props {
    authUser: IAuthUserProfile
    workoutData: IWorkoutData
  }
  const props = defineProps<Props>()
  const { authUser, workoutData } = toRefs(props)

  const emit = defineEmits(['getCoordinates'])

  const { t } = useI18n()

  const { darkTheme } = useApp()

  const displayDistance: Ref<boolean> = ref(true)

  const plugins = [htmlLegendPlugin]
  const fromKmUnit = getUnitTo('km')
  const fromMUnit = getUnitTo('m')

  const beginElevationAtZero: ComputedRef<boolean> = computed(
    () => authUser.value.start_elevation_at_zero
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
  const chartData: ComputedRef<ChartData<'line'>> = computed(() => ({
    labels: displayDistance.value
      ? datasets.value.distance_labels
      : datasets.value.duration_labels,
    datasets: JSON.parse(
      JSON.stringify([
        datasets.value.datasets.speed,
        datasets.value.datasets.elevation,
      ])
    ),
  }))
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
              : formatDuration(value)
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
      ySpeed: {
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
          text: t('workouts.SPEED') + ` (${fromKmUnit}/h)`,
          ...textColors.value,
        },
        ticks: {
          ...textColors.value,
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
        position: 'right',
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
          label: function (context) {
            const label = ` ${context.dataset.label}: ${context.formattedValue}`
            return context.dataset.yAxisID === 'yElevation'
              ? label + ` ${fromMUnit}`
              : label + ` ${fromKmUnit}/h`
          },
          title: function (tooltipItems) {
            if (tooltipItems.length > 0) {
              emitCoordinates(coordinates.value[tooltipItems[0].dataIndex])
            }
            return tooltipItems.length === 0
              ? ''
              : displayDistance.value
                ? `${t('workouts.DISTANCE')}: ${
                    tooltipItems[0].label
                  } ${fromKmUnit}`
                : `${t('workouts.DURATION')}: ${formatDuration(
                    tooltipItems[0].label.replace(',', '')
                  )}`
          },
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
  function formatDuration(duration: string | number): string {
    return new Date(+duration * 1000).toISOString().substr(11, 8)
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
