import type { GeoJSON } from 'geojson'

import type { TPaginationPayload } from '@/types/api'
import type { IChartDataset } from '@/types/chart'
import type { IEquipment, ILightEquipment } from '@/types/equipments'
import type { TCoordinates } from '@/types/map'
import type {
  IUserReportAction,
  IUserLightProfile,
  IUserProfile,
  TVisibilityLevels,
} from '@/types/user'

export type TFileExtension = 'fit' | 'gpx' | 'kml' | 'tcx'

export interface IWorkoutSegment {
  ascent: number
  ave_cadence: number | null
  ave_hr: number | null
  ave_pace: string | null
  ave_power: number | null
  ave_speed: number
  descent: number
  distance: number
  duration: string
  max_alt: number
  max_cadence: number | null
  max_hr: number | null
  max_pace: string | null
  max_power: number | null
  max_speed: number
  min_alt: number
  moving: string
  pauses: string
  segment_id: string
  segment_number: number
  workout_id: string
}

export interface ICardRecord {
  id: number
  value: number | string
  workout_date: string
  workout_id: string
  label: string
}

export type TRecordType = 'AP' | 'AS' | 'FD' | 'HA' | 'LD' | 'MP' | 'MS'

export interface IRecord {
  id: number
  record_type: TRecordType
  sport_id: number
  user: string
  value: number | string
  workout_date: string
  workout_id: string
}

export interface IRecordsBySport {
  [key: string]: string | IRecord[] | null
  label: string
  color: string | null
  records: IRecord[]
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
  windBearing?: number
}

export interface IMapWorkout {
  bounds: number[]
  id: string
  sport_id: number
  title: string
  workout_date: string
  workout_visibility: TVisibilityLevels
}

export interface IWorkout {
  analysis_visibility?: TVisibilityLevels
  ascent: number | null
  ave_cadence: number | null
  ave_hr: number | null
  ave_pace: string | null
  ave_power: number | null
  ave_speed: number | null
  bounds: number[]
  creation_date: string | null
  descent: number | null
  description: string
  distance: number | null
  duration: string | null
  equipments: IEquipment[] | ILightEquipment[]
  id: string
  liked: boolean
  likes_count: number
  map: string | null
  map_visibility?: TVisibilityLevels
  max_alt: number | null
  max_cadence: number | null
  max_hr: number | null
  max_pace: string | null
  max_power: number | null
  max_speed: number | null
  min_alt: number | null
  modification_date: string | null
  moving: string | null
  next_workout: string | null
  notes: string
  original_file: TFileExtension | null
  pauses: string | null
  previous_workout: string | null
  records: IRecord[]
  segments: IWorkoutSegment[]
  source?: string | null
  sport_id: number
  suspended?: boolean
  suspended_at?: string | null
  suspension?: IUserReportAction
  title: string
  user: IUserProfile
  weather_end: IWeather | null
  weather_start: IWeather | null
  with_analysis: boolean
  with_file: boolean
  with_geometry?: boolean
  workout_date: string
  workout_visibility?: TVisibilityLevels
}

export interface IWorkoutObject {
  analysisVisibility: TVisibilityLevels | null | undefined
  ascent: number | null
  aveCadence: number | null
  aveHr: number | null
  avePower: number | null
  avePace: string | null
  aveSpeed: number | null
  descent: number | null
  distance: number | null
  duration: string | null
  equipments: IEquipment[] | ILightEquipment[] | null
  liked: boolean
  likes_count: number
  maxAlt: number | null
  maxCadence: number | null
  maxHr: number | null
  maxPace: string | null
  maxPower: number | null
  maxSpeed: number | null
  mapVisibility: TVisibilityLevels | null | undefined
  minAlt: number | null
  moving: string | null
  nextUrl: string | null
  originalFile: TFileExtension | null
  pauses: string | null
  previousUrl: string | null
  records: IRecord[]
  segmentId: string | null
  segmentNumber: number | null
  source: string | null
  suspended: boolean
  title: string
  type: string
  workoutDate: string
  weatherEnd: IWeather | null
  workoutFullDate: string
  weatherStart: IWeather | null
  with_analysis: boolean
  with_file: boolean
  workoutId: string
  workoutTime: string
  workoutVisibility: TVisibilityLevels | null | undefined
}

export interface IWorkoutForm {
  sport_id: number | null
  notes: string
  title: string
  workout_date?: string
  distance?: number
  duration?: number
  file?: Blob
  ascent?: number | null
  descent?: number | null
  equipment_ids: string[]
  description: string
  analysis_visibility?: TVisibilityLevels
  map_visibility?: TVisibilityLevels
  workout_visibility: TVisibilityLevels
}

export interface IWorkoutPayload {
  workoutId: string | string[]
  segmentId?: string | string[]
  data?: IWorkoutForm
}

export type IWorkoutContentType = 'NOTES' | 'DESCRIPTION'

export interface IWorkoutContentEdition {
  loading: boolean
  contentType: IWorkoutContentType | ''
}

export interface IWorkoutContentPayload {
  workoutId: string | string[]
  content: string
  contentType: IWorkoutContentType
}

export type TWorkoutsPayload = TPaginationPayload & {
  from?: string
  to?: string
  ave_speed_from?: string
  ave_speed_to?: string
  max_speed_from?: string
  max_speed_to?: string
  distance_from?: string
  distance_to?: string
  duration_from?: string
  duration_to?: string
  sport_id?: string
}

export type TMapParamsKeys = 'to' | 'from' | 'sport_ids'
export type TWorkoutsMapPayload = {
  [key in TMapParamsKeys]?: string
}

export interface IWorkoutApiChartData {
  cadence?: number
  distance: number
  duration: number
  elevation?: number
  hr?: number
  latitude: number
  longitude: number
  pace?: number
  power?: number
  speed: number
  time: string
}

export interface ICurrentCommentEdition {
  type?: string
  comment?: IComment
}

export interface IWorkoutData {
  geojson: GeoJSON | null
  gpx: string
  loading: boolean
  workout: IWorkout
  chartData: IWorkoutApiChartData[]
  chartDataLoading: boolean
  comments: IComment[]
  commentsLoading: string | null
  currentCommentEdition: ICurrentCommentEdition
  currentReporting: boolean
  refreshLoading: boolean
}

export type TWorkoutDatasetKeys =
  | 'speed'
  | 'elevation'
  | 'hr'
  | 'cadence'
  | 'power'
  | 'pace'

export type TWorkoutDatasets = {
  [key in TWorkoutDatasetKeys]: IChartDataset
}

export interface IWorkoutChartData {
  distance_labels: unknown[]
  duration_labels: unknown[]
  datasets: TWorkoutDatasets
  coordinates: TCoordinates[]
}

export interface IDuration {
  days: string
  duration: string
}

export interface IComment {
  created_at: string
  id: string
  liked: boolean
  likes_count: number
  mentions: IUserProfile[]
  modification_date: string | null
  suspended?: boolean
  suspended_at?: string | null
  suspension?: IUserReportAction
  text: string | null
  text_html: string | null
  text_visibility: TVisibilityLevels
  user: IUserLightProfile
  workout_id: string
}

export interface ICommentForm {
  id?: string
  text: string
  text_visibility?: TVisibilityLevels
  workout_id: string
}

export interface ICommentPayload {
  workoutId: string
  commentId: string
}

export interface ILikesPayload {
  objectId: string
  objectType: 'comment' | 'workout'
  page: number
}

export interface IAppealPayload {
  objectId: string
  objectType: 'comment' | 'workout'
  text: string
}

export interface TWorkoutsStatistic {
  average_ascent: number | null
  average_descent: number | null
  average_distance: number | null
  average_duration: string | null
  average_pace: string | null
  average_speed: number | null
  count: number
  max_pace: string | null
  max_speed: number | null
  total_ascent: number | null
  total_descent: number | null
  total_distance: number | null
  total_duration: string | null
  total_sports: number
}

export type TWorkoutsStatistics = {
  [key: string]: TWorkoutsStatistic
  current_page: TWorkoutsStatistic
  all: TWorkoutsStatistic
}

export interface IWorkoutFilesError {
  createdWorkouts: number
  erroredWorkouts: Record<string, string>
}

export interface ILocation {
  addresstype: string
  coordinates: string
  display_name: string
  name: string
  osm_id: string
}
