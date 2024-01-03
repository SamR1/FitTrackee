import { describe, it, expect } from 'vitest'

import { TUnit } from '@/types/units'
import { convertDistance, getTemperature, getWindSpeed } from '@/utils/units'

describe('convertDistance', () => {
  const testsParams: [number, TUnit, TUnit, number][] = [
    [0, 'm', 'ft', 0],
    [5, 'm', 'ft', 16.404],
    [5, 'm', 'mi', 0.003],
    [5, 'm', 'm', 5.0],
    [5, 'm', 'km', 0.005],
    [5, 'km', 'ft', 16404.199],
    [5, 'km', 'mi', 3.107],
    [5, 'km', 'm', 5000.0],
    [5, 'km', 'km', 5.0],
    [5, 'ft', 'ft', 5.0],
    [5, 'ft', 'mi', 0.001],
    [5, 'ft', 'm', 1.524],
    [5, 'ft', 'km', 0.002],
    [5, 'mi', 'ft', 26400.0],
    [5, 'mi', 'mi', 5.0],
    [5, 'mi', 'm', 8046.72],
    [5, 'mi', 'km', 8.047],
  ]

  testsParams.map((testParams) => {
    it(`convert ${testParams[0]}${testParams[1]} in ${testParams[2]}}`, () => {
      expect(convertDistance(testParams[0], testParams[1], testParams[2])).toBe(
        testParams[3]
      )
    })
  })
})

describe('convertDistance w/ digits', () => {
  const testsParams: [number, TUnit, TUnit, number | null, number][] = [
    [5, 'km', 'mi', null, 3.106855961174243],
    [5, 'km', 'mi', 0, 3],
    [5, 'km', 'mi', 1, 3.1],
    [5, 'km', 'mi', 2, 3.11],
  ]

  testsParams.map((testParams) => {
    it(`convert ${testParams[0]}${testParams[1]} in ${testParams[2]}}`, () => {
      expect(
        convertDistance(
          testParams[0],
          testParams[1],
          testParams[2],
          testParams[3]
        )
      ).toBe(testParams[4])
    })
  })
})

describe('getTemperature', () => {
  const testsParams: [number, boolean, string][] = [
    [0, false, '0°C'],
    [10.0, false, '10.0°C'],
    [10.3, false, '10.3°C'],
    [0, true, '32.0 °F'],
    [13.0, true, '55.4 °F'],
  ]

  testsParams.map((testParams) => {
    it(`get temperature for input: ${testParams[0]} and imperialUnits: ${testParams[1]}`, () => {
      expect(getTemperature(testParams[0], testParams[1])).toBe(testParams[2])
    })
  })
})

describe('getWindSpeed', () => {
  const testsParams: [number, boolean, string][] = [
    [0, false, '0m/s'],
    [6.0, false, '6.0m/s'],
    [6.3, false, '6.3m/s'],
    [0, true, '0 mph'],
    [13.2, true, '29.5 mph'],
  ]

  testsParams.map((testParams) => {
    it(`get wind speed for input: ${testParams[0]} and imperialUnits: ${testParams[1]}`, () => {
      expect(getWindSpeed(testParams[0], testParams[1])).toBe(testParams[2])
    })
  })
})
