import type { TCoordinates } from '@/types/map'
import type {
  IWorkout,
  IWorkoutApiChartData,
  IWorkoutChartData,
  TWorkoutDatasets,
} from '@/types/workouts'
import { convertStatsDistance } from '@/utils/units'

export const chartsColors = {
  ligthMode: {
    // default chartjs values
    text: '#666',
    line: 'rgba(0, 0, 0, 0.1)',
  },
  darkMode: {
    text: '#a1a1a1',
    line: '#3f3f3f',
  },
}

export const getDatasets = (
  chartData: IWorkoutApiChartData[],
  t: CallableFunction,
  useImperialUnits: boolean,
  useDarkMode: boolean = false
): IWorkoutChartData => {
  const datasets: TWorkoutDatasets = {
    speed: {
      label: t('workouts.SPEED'),
      backgroundColor: ['transparent'],
      borderColor: [useDarkMode ? '#5f5c97' : '#8884d8'],
      borderWidth: 2,
      data: [],
      yAxisID: 'ySpeed',
    },
    elevation: {
      label: t('workouts.ELEVATION'),
      backgroundColor: [useDarkMode ? '#303030' : '#e5e5e5'],
      borderColor: [useDarkMode ? '#222222' : '#cccccc'],
      borderWidth: 1,
      fill: true,
      data: [],
      yAxisID: 'yElevation',
    },
  }
  const distance_labels: unknown[] = []
  const duration_labels: unknown[] = []
  const coordinates: TCoordinates[] = []

  chartData.map((data) => {
    distance_labels.push(
      convertStatsDistance('km', data.distance, useImperialUnits)
    )
    duration_labels.push(data.duration)
    datasets.speed.data.push(
      convertStatsDistance('km', data.speed, useImperialUnits)
    )
    if (data.elevation !== undefined) {
      datasets.elevation.data.push(
        convertStatsDistance('m', data.elevation, useImperialUnits)
      )
    }
    coordinates.push({ latitude: data.latitude, longitude: data.longitude })
  })

  return { distance_labels, duration_labels, datasets, coordinates }
}

export const getDonutDatasets = (
  workouts: IWorkout[]
): Record<number, Record<string, number>> => {
  const total = workouts.length
  if (total === 0) {
    return {}
  }

  const datasets: Record<number, Record<string, number>> = {}
  workouts.map((workout) => {
    if (!datasets[workout.sport_id]) {
      datasets[workout.sport_id] = {
        count: 0,
        percentage: 0,
      }
    }
    datasets[workout.sport_id].count += 1
    datasets[workout.sport_id].percentage =
      datasets[workout.sport_id].count / total
  })

  return datasets
}

export const defaultOrder = {
  order: 'desc',
  order_by: 'workout_date',
}
