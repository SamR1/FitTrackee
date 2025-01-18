export type TCenter = number[]

export type TBounds = number[][]

export type TCoordinatesKeys = 'latitude' | 'longitude'
export type TCoordinates = {
  [key in TCoordinatesKeys]: number | null
}

export interface ILeafletObject {
  leafletObject: { fitBounds: (bounds: TBounds) => void }
}
