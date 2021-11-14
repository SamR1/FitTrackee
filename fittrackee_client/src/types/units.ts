export type TUnitSystem = 'imperial' | 'metric'

export type TUnit = 'ft' | 'mi' | 'm' | 'km'

export type TFactor = {
  [k in string]: Record<string, number>
}

export interface IUnit {
  unit: TUnit
  system: TUnitSystem
  multiplier: number
}
