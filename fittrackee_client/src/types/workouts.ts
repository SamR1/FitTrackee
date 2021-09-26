import { IChartDataset } from '@/types/chart'

export interface IWorkoutSegment {
  ascent: number
  ave_speed: number
  descent: number
  distance: number
  duration: string
  max_alt: number
  max_speed: number
  min_alt: number
  moving: string
  pauses: string
  segment_id: number
  workout_id: string
}

export interface IRecord {
  id: number
  record_type: string
  sport_id: number
  user: string
  value: number | string
  workout_date: string
  workout_id: string
}

export interface IRecordsBySport {
  [key: string]: string | Record<string, string | number>[]
  img: string
  records: Record<string, string | number>[]
}

export interface IRecordsBySports {
  [key: string]: IRecordsBySport
}

export interface IWeather {
  humidity: number
  icon: string
  summary: string
  temperature: number
  wind: number
}

export interface IWorkout {
  ascent: number | null
  ave_speed: number
  bounds: number[]
  creation_date: string
  descent: number | null
  distance: number
  duration: string
  id: string
  map: string | null
  max_alt: number | null
  max_speed: number
  min_alt: number | null
  modification_date: string | null
  moving: string
  next_workout: string | null
  notes: string
  pauses: string | null
  previous_workout: string | null
  records: IRecord[]
  segments: IWorkoutSegment[]
  sport_id: number
  title: string
  user: string
  weather_end: IWeather | null
  weather_start: IWeather | null
  with_gpx: boolean
  workout_date: string
}

export interface IWorkoutsPayload {
  from?: string
  to?: string
  order?: string
  per_page?: number
  page?: number
}

export interface IWorkoutApiChartData {
  distance: number
  duration: number
  elevation: number
  latitude: number
  longitude: number
  speed: number
  time: string
}

export interface IWorkoutData {
  gpx: string
  loading: boolean
  workout: IWorkout
  chartData: IWorkoutApiChartData[]
}

export type TWorkoutDatasetKeys = 'speed' | 'elevation'

export type TWorkoutDatasets = {
  [key in TWorkoutDatasetKeys]: IChartDataset
}

export type TCoordinatesKeys = 'latitude' | 'longitude'

export type TCoordinates = {
  [key in TCoordinatesKeys]: number | null
}

export interface IWorkoutChartData {
  distance_labels: unknown[]
  duration_labels: unknown[]
  datasets: TWorkoutDatasets
  coordinates: TCoordinates[]
}
