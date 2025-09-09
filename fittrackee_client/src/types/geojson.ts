import type { IWorkout } from '@/types/workouts.ts'

export interface ILineString {
  coordinates: number[][]
  type: 'LineString'
}

export interface IMultiLineString {
  coordinates: ILineString['coordinates'][]
  type: 'MultiLineString'
}

export interface IWorkoutFeature {
  properties: IWorkout
  geometry: IMultiLineString
  type: 'Feature'
}

export interface IWorkoutsFeatureCollection {
  bbox: number[]
  features: IWorkoutFeature[]
  type: 'FeatureCollection'
}
