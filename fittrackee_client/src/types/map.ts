import type { IHeatmapOverlay } from '@/types/heatmap.ts'

export type TCenter = number[]

export type TBounds = number[][]

export type TCoordinatesKeys = 'latitude' | 'longitude'
export type TCoordinates = {
  [key in TCoordinatesKeys]: number | null
}

export interface ILeafletObject {
  leafletObject: {
    fitBounds: (bounds: TBounds) => void
    addLayer: (layer: IHeatmapOverlay) => void
    removeLayer: (layer: IHeatmapOverlay) => void
  }
}
