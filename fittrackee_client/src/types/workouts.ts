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
  value: number
  workout_date: string
  workout_id: string
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
