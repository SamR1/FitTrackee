<template>
  <div id="workout-chart">
    <Card :without-title="false">
      <template #title>{{ t('workouts.ANALYSIS') }} </template>
      <template #content>
        <div class="chart-radio">
          <label>
            <input
              type="radio"
              name="distance"
              :checked="displayDistance"
              @click="updateDisplayDistance"
            />
            {{ t('workouts.DISTANCE') }}
          </label>
          <label>
            <input
              type="radio"
              name="duration"
              :checked="!displayDistance"
              @click="updateDisplayDistance"
            />
            {{ t('workouts.DURATION') }}
          </label>
        </div>
        <LineChart v-bind="lineChartProps" class="line-chart" />
        <div class="no-data-cleaning">
          {{ t('workouts.NO_DATA_CLEANING') }}
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { ChartData, ChartOptions } from 'chart.js'
  import { PropType, defineComponent, ref, ComputedRef, computed } from 'vue'
  import { LineChart, useLineChart } from 'vue-chart-3'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkoutChartData, IWorkoutState } from '@/types/workouts'
  import { getDatasets } from '@/utils/workouts'

  export default defineComponent({
    name: 'WorkoutChart',
    components: {
      Card,
      LineChart,
    },
    props: {
      authUser: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
      workout: {
        type: Object as PropType<IWorkoutState>,
        required: true,
      },
    },
    setup(props) {
      const { t } = useI18n()
      let displayDistance = ref(true)
      const datasets: ComputedRef<IWorkoutChartData> = computed(() =>
        getDatasets(props.workout.chartData, t)
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
      const options = computed<ChartOptions<'line'>>(() => ({
        responsive: true,
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
                return tooltipItems.length === 0
                  ? ''
                  : displayDistance.value
                  ? tooltipItems[0].label + ' km'
                  : formatDuration(tooltipItems[0].label.replace(',', ''))
              },
            },
          },
        },
      }))

      function updateDisplayDistance() {
        displayDistance.value = !displayDistance.value
      }
      function formatDuration(duration: string | number): string {
        return new Date(+duration * 1000).toISOString().substr(11, 8)
      }

      const { lineChartProps } = useLineChart({
        chartData,
        options,
      })
      return {
        displayDistance,
        lineChartProps,
        t,
        updateDisplayDistance,
      }
    },
  })
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
    }
  }
</style>
