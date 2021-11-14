import { IUnit, TFactor, TUnit } from '@/types/units'

export const units: Record<string, IUnit> = {
  ft: {
    unit: 'ft',
    system: 'imperial',
    multiplier: 1,
    defaultTarget: 'm',
  },
  mi: {
    unit: 'mi',
    system: 'imperial',
    multiplier: 5280,
    defaultTarget: 'km',
  },
  m: {
    unit: 'm',
    system: 'metric',
    multiplier: 1,
    defaultTarget: 'ft',
  },
  km: {
    unit: 'm',
    system: 'metric',
    multiplier: 1000,
    defaultTarget: 'mi',
  },
}

const factors: TFactor = {
  metric: {
    imperial: 3.280839895,
    metric: 1,
  },
  imperial: {
    metric: 1 / 3.280839895,
    imperial: 1,
  },
}

export const convertDistance = (
  distance: number,
  from: TUnit,
  to: TUnit,
  digits: number | null = 3
): number => {
  const unitFrom = units[from]
  const unitTo = units[to]
  const convertedDistance =
    (distance * unitFrom.multiplier * factors[unitFrom.system][unitTo.system]) /
    unitTo.multiplier
  if (digits !== null) {
    return parseFloat(convertedDistance.toFixed(digits))
  }
  return convertedDistance
}
