export interface IStatisticsParams {
  from: string
  to: string
  time: string
}

export interface IUserStatisticsPayload {
  username: string
  filterType: string
  params: IStatisticsParams
}

export interface IStatisticsDateParams {
  duration: string
  start: Date
  end: Date
}

export type TDatasetKeys = 'nb_workouts' | 'total_duration' | 'total_distance'

export type TStatistics = Record<TDatasetKeys, number>

export type TSportStatistics = {
  [key in number]: TStatistics
}

export type TStatisticsFromApi = {
  [key in string]: TSportStatistics
}

export interface IStatisticsChartDataset {
  label: string
  backgroundColor: string[]
  data: number[]
}

export type TStatisticsDatasets = Record<
  TDatasetKeys,
  IStatisticsChartDataset[]
>

export interface IStatisticsChartData {
  labels: unknown[]
  datasets: TStatisticsDatasets
}
