import {
  IWorkoutApiChartData,
  IWorkoutChartData,
  TCoordinates,
  TWorkoutDatasets,
} from '@/types/workouts'

export const getDatasets = (
  chartData: IWorkoutApiChartData[],
  t: CallableFunction
): IWorkoutChartData => {
  const datasets: TWorkoutDatasets = {
    speed: {
      label: t('workouts.SPEED'),
      backgroundColor: ['#FFFFFF'],
      borderColor: ['#8884d8'],
      borderWidth: 2,
      data: [],
      yAxisID: 'ySpeed',
    },
    elevation: {
      label: t('workouts.ELEVATION'),
      backgroundColor: ['#e5e5e5'],
      borderColor: ['#cccccc'],
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
    distance_labels.push(data.distance)
    duration_labels.push(data.duration)
    datasets.speed.data.push(data.speed)
    datasets.elevation.data.push(data.elevation)
    coordinates.push({ latitude: data.latitude, longitude: data.longitude })
  })

  return { distance_labels, duration_labels, datasets, coordinates }
}
