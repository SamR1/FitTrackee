import type { IChartDataset } from '@/types/chart'

export type TStatisticsTimeFrame = 'week' | 'month' | 'year'

export type TStatisticsType = 'average' | 'total'

export interface IStatisticsParams {
  from: string
  to: string
  time: string
  type: TStatisticsType
}

export interface IUserStatisticsPayload {
  username: string
  filterType: string
  params: IStatisticsParams
}

export interface IStatisticsDateParams {
  duration: TStatisticsTimeFrame
  start: Date
  end: Date
  statsType: TStatisticsType
}

export type TStatisticsDatasetKeys =
  | 'average_ascent'
  | 'average_descent'
  | 'average_distance'
  | 'average_duration'
  | 'average_speed'
  | 'average_workouts'
  | 'total_workouts'
  | 'total_duration'
  | 'total_distance'
  | 'total_ascent'
  | 'total_descent'

export type TStatistics = {
  [key in TStatisticsDatasetKeys]: number
}

export type TSportStatistics = {
  [key in number]: TStatistics
}

export type TStatisticsFromApi = {
  [key in string]: TSportStatistics
}

export type TStatisticsDatasets = {
  [key in TStatisticsDatasetKeys]: IChartDataset[]
}

export type TStatisticsWorkoutsAverageDatasets = {
  workouts_average: IChartDataset[]
}

export interface IStatisticsChartData {
  labels: unknown[]
  datasets: TStatisticsDatasets
}

export interface IStatisticsWorkoutsAverageChartData {
  labels: string[]
  datasets: TStatisticsWorkoutsAverageDatasets
  workoutsAverage: number
}
