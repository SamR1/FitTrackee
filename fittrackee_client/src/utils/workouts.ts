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
      id: 'speed',
      label: t('workouts.SPEED'),
      backgroundColor: ['transparent'],
      borderColor: [useDarkMode ? '#5f5c97' : '#8884d8'],
      borderWidth: 2,
      data: [],
      yAxisID: 'yLeft',
    },
    elevation: {
      id: 'elevation',
      label: t('workouts.ELEVATION'),
      backgroundColor: [useDarkMode ? '#303030' : '#e5e5e5'],
      borderColor: [useDarkMode ? '#222222' : '#cccccc'],
      borderWidth: 1,
      fill: true,
      data: [],
      yAxisID: 'yRight',
    },
    hr: {
      id: 'hr',
      label: t('workouts.HEART_RATE'),
      backgroundColor: ['transparent'],
      borderColor: [useDarkMode ? '#b41e4a' : '#ec1f5e'],
      borderWidth: 1,
      data: [],
      yAxisID: 'yLeft',
    },
    cadence: {
      id: 'cadence',
      label: t('workouts.CADENCE'),
      backgroundColor: ['transparent'],
      borderColor: [useDarkMode ? '#989898' : '#494949'],
      borderWidth: 1,
      data: [],
      yAxisID: 'yLeft',
    },
  }
  const distance_labels: unknown[] = []
  const duration_labels: unknown[] = []
  const coordinates: TCoordinates[] = []

  chartData.forEach((data) => {
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
    if (data.hr !== undefined) {
      datasets.hr.data.push(data.hr)
    }
    if (data.cadence !== undefined) {
      datasets.cadence.data.push(data.cadence)
    }
    coordinates.push({ latitude: data.latitude, longitude: data.longitude })
  })

  if (datasets.elevation.data.length == 0) {
    if (datasets.hr.data.length > 0) {
      datasets.hr.yAxisID = 'yRight'
    } else if (datasets.cadence.data.length > 0) {
      datasets.cadence.yAxisID = 'yRight'
    }
  }

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
  workouts.forEach((workout) => {
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
