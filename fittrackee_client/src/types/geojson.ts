import type { MultiLineString, Point } from 'geojson'

import type { IMapWorkout } from '@/types/workouts.ts'

export interface IWorkoutFeature {
  properties: IMapWorkout
  geometry: MultiLineString | Point
  type: 'Feature'
}

export interface IWorkoutsFeatureCollection {
  bbox: number[]
  features: IWorkoutFeature[]
  limit_exceeded?: boolean
  type: 'FeatureCollection'
}
