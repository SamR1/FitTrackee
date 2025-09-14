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
