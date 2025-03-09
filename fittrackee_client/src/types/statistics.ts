import type { IChartDataset } from '@/types/chart'

export type TStatisticsTimeFrame = 'day' | 'week' | 'month' | 'year'

export type TStatisticsType = 'average' | 'total'

export interface IStatisticsParams {
  from: string
  to: string
  time: string
  type: TStatisticsType
}

export interface IUserStatisticsPayload {
  username: string
  params: IStatisticsParams
}

export interface IUserSportStatisticsPayload {
  username: string
  sportId: number
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

export type TStatisticsTypes = 'by_time' | 'by_sport'

export type TStatistics = {
  [key in TStatisticsDatasetKeys]: number
}

export type TSportStatistics = {
  [key in number]: TStatistics
}

export type TStatisticsFromApi = {
  [key in string]: TSportStatistics
}

export type TStatisticsForSport = {
  average_ascent: number | null
  average_descent: number | null
  average_distance: number
  average_duration: string
  average_speed: number
  average_workouts: number
  total_workouts: number
  total_duration: string
  total_distance: number
  total_ascent: number | null
  total_descent: number | null
}
export type TSportStatisticsFromApi = {
  [key in string]: TStatisticsForSport
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
