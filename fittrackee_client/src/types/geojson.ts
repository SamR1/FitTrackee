import type { MultiLineString } from 'geojson'

import type { IMapWorkout } from '@/types/workouts.ts'

export interface IWorkoutFeature {
  properties: IMapWorkout
  geometry: MultiLineString
  type: 'Feature'
}

export interface IWorkoutsFeatureCollection {
  bbox: number[]
  features: IWorkoutFeature[]
  type: 'FeatureCollection'
}
