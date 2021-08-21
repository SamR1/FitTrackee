export interface IStatistics {
  nb_workouts: number
  total_distance: number
  total_duration: number
}
export type TStatistics = {
  [key in string | number]: IStatistics
}

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
