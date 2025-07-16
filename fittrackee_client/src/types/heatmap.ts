import type { IWorkoutApiChartData } from '@/types/workouts.ts'

export interface IHeatmapData {
  max: number
  data: IWorkoutApiChartData[]
}

export interface IHeatmapOverlay {
  setData(data: IHeatmapData): void
}
