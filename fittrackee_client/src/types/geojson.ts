export interface TPoint {
  longitude: number
  latitude: number
  elevation?: number
}

export interface ILineString {
  coordinates: TPoint[]
  type: 'LineString'
}

export interface IMultiLineString {
  coordinates: ILineString['coordinates'][]
  type: 'MultiLineString'
}
