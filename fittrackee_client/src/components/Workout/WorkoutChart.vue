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
        <LineChart
          v-bind="lineChartProps"
          class="line-chart"
          @mouseleave="emitEmptyCoordinates"
        />
        <div class="no-data-cleaning">
          {{ $t('workouts.NO_DATA_CLEANING') }}
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { ChartData, ChartOptions } from 'chart.js'
  import { ComputedRef, computed, ref } from 'vue'
  import { LineChart, useLineChart } from 'vue-chart-3'
  import { useI18n } from 'vue-i18n'

  import { IUserProfile } from '@/types/user'
  import {
    IWorkoutChartData,
    IWorkoutData,
    TCoordinates,
  } from '@/types/workouts'
  import { getDatasets } from '@/utils/workouts'

  interface Props {
    authUser: IUserProfile
    workoutData: IWorkoutData
  }
  const props = defineProps<Props>()

  const emit = defineEmits(['getCoordinates'])

  const { t } = useI18n()

  let displayDistance = ref(true)
  const datasets: ComputedRef<IWorkoutChartData> = computed(() =>
    getDatasets(props.workoutData.chartData, t)
  )
  let chartData: ComputedRef<ChartData<'line'>> = computed(() => ({
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
  const options = computed<ChartOptions<'line'>>(() => ({
    responsive: true,
    maintainAspectRatio: true,
    animation: false,
    layout: {
      padding: {
        top: 22,
      },
    },
    scales: {
      [displayDistance.value ? 'xDistance' : 'xDuration']: {
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          count: 10,
          callback: function (value) {
            return displayDistance.value
              ? Number(value).toFixed(2)
              : formatDuration(value)
          },
        },
        type: 'linear',
        bounds: 'data',
        title: {
          display: true,
          text: displayDistance.value
            ? t('workouts.DISTANCE') + ' (km)'
            : t('workouts.DURATION'),
        },
      },
      ySpeed: {
        grid: {
          drawOnChartArea: false,
        },
        position: 'left',
        title: {
          display: true,
          text: t('workouts.SPEED') + ' (km/h)',
        },
      },
      yElevation: {
        beginAtZero: true,
        grid: {
          drawOnChartArea: false,
        },
        position: 'right',
        title: {
          display: true,
          text: t('workouts.ELEVATION') + ' (m)',
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
              ? label + ' m'
              : label + ' km/h'
          },
          title: function (tooltipItems) {
            if (tooltipItems.length > 0) {
              emitCoordinates(coordinates.value[tooltipItems[0].dataIndex])
            }
            return tooltipItems.length === 0
              ? ''
              : displayDistance.value
              ? `${t('workouts.DISTANCE')}: ${tooltipItems[0].label} km`
              : `${t('workouts.DURATION')}: ${formatDuration(
                  tooltipItems[0].label.replace(',', '')
                )}`
          },
        },
      },
    },
  }))
  const { lineChartProps } = useLineChart({
    chartData,
    options,
  })

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
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
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
        .no-data-cleaning {
          font-size: 0.85em;
          font-style: italic;
        }
      }

      @media screen and (max-width: $small-limit) {
        .card-content {
          padding: $default-padding 0;
          .no-data-cleaning {
            padding: 0 $default-padding * 2;
          }
        }
      }
    }
  }
</style>
