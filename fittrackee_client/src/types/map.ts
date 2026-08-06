import type { Map } from 'leaflet'

export type TCoordinatesKeys = 'latitude' | 'longitude'
export type TCoordinates = {
  [key in TCoordinatesKeys]: number | null
}

export interface ILeafletObject {
  leafletObject: Map
}

export interface IGeoJsonOptions {
  weight?: number
}

// what the API returns: [i, j, workouts count] per cell, and the size the
// cells were merged to, in meters in Web Mercator
export interface IHeatmapCells {
  cells: number[][]
  cell_size: number
}

export interface IHeatmapCell {
  color: string
  west: number
  south: number
  east: number
  north: number
}
