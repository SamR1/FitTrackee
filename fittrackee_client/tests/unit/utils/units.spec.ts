import { assert } from 'chai'

import { TUnit } from '@/types/units'
import { convertDistance } from '@/utils/units'

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
      assert.equal(
        convertDistance(testParams[0], testParams[1], testParams[2]),
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
      assert.equal(
        convertDistance(
          testParams[0],
          testParams[1],
          testParams[2],
          testParams[3]
        ),
        testParams[4]
      )
    })
  })
})
