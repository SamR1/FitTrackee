import { describe, it, expect } from 'vitest'

import { convertDegreeToDirection } from '@/utils/weather'

describe('convertDegreeToDirection', () => {
  const testsParams: [number, string][] = [
    [0, 'N'],
    [45, 'NE'],
    [90, 'E'],
    [135, 'SE'],
    [180, 'S'],
    [225, 'SW'],
    [270, 'W'],
    [315, 'NW'],
    [22, 'NNE'],
    [359, 'N'],
  ]
  testsParams.map((testParams) => {
    it(`convert ${testParams[0]}° to ${testParams[1]}`, () => {
      expect(convertDegreeToDirection(testParams[0])).toBe(testParams[1])
    })
  })
})
