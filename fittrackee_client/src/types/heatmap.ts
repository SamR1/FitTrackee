import type { Layer } from 'leaflet'

import type { IWorkoutApiChartData } from '@/types/workouts.ts'

export interface IHeatmapData {
  max: number
  data: IWorkoutApiChartData[]
}

export interface IHeatmapOverlay extends Layer {
  setData(data: IHeatmapData): void
}
