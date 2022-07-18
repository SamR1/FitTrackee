import { assert } from 'chai'

import { datasetKeys } from '@/utils/statistics'
import { formatTooltipValue } from '@/utils/tooltip'

describe('formatTooltipValue', () => {
  const testsParams = [
    {
      description: 'returns 3 if input is average speed',
      inputDisplayedData: datasetKeys[0], // 'average_speed'
      inputValue: 30,
      expectedResult: '30.00 km/h',
    },
    {
      description: 'returns 3 if input is workouts count',
      inputDisplayedData: datasetKeys[1], // 'nb_workouts'
      inputValue: 30,
      expectedResult: '30',
    },
    {
      description: 'returns 00m:03s if input is total duration',
      inputDisplayedData: datasetKeys[2], // 'total_duration'
      inputValue: 30,
      expectedResult: '00m 30s',
    },
    {
      description: 'returns 3.00 km if input is total distance',
      inputDisplayedData: datasetKeys[3], // 'total_distance'
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 30 m if input is total ascent',
      inputDisplayedData: datasetKeys[4], // 'total_ascent'
      inputValue: 30,
      expectedResult: '30 m',
    },
    {
      description: 'returns 30 m if input is total descent',
      inputDisplayedData: datasetKeys[5], // 'total_descent'
      inputValue: 30,
      expectedResult: '30 m',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.equal(
        formatTooltipValue(
          testParams.inputDisplayedData,
          testParams.inputValue,
          false
        ),
        testParams.expectedResult
      )
    })
  })
})

describe('formatTooltipValue after conversion to imperial units', () => {
  const testsParams = [
    {
      description: 'returns 30 if input is average speed',
      inputDisplayedData: datasetKeys[0], // 'average_speed'
      inputValue: 30,
      expectedResult: '30.00 mi/h',
    },
    {
      description: 'returns 30 if input is workouts count',
      inputDisplayedData: datasetKeys[1], // 'nb_workouts'
      inputValue: 30,
      expectedResult: '30',
    },
    {
      description: 'returns 00m:03s if input is total duration',
      inputDisplayedData: datasetKeys[2], // 'total_duration'
      inputValue: 30,
      expectedResult: '00m 30s',
    },
    {
      description: 'returns 30 mi if input is total distance',
      inputDisplayedData: datasetKeys[3], // 'total_distance'
      inputValue: 30,
      expectedResult: '30.00 mi',
    },
    {
      description: 'returns 98.43 ft if input is total ascent',
      inputDisplayedData: datasetKeys[4], // 'total_ascent'
      inputValue: 30,
      expectedResult: '98.43 ft',
    },
    {
      description: 'returns 98.43 ft if input is total descent',
      inputDisplayedData: datasetKeys[5], // 'total_descent'
      inputValue: 30,
      expectedResult: '98.43 ft',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.equal(
        formatTooltipValue(
          testParams.inputDisplayedData,
          testParams.inputValue,
          true
        ),
        testParams.expectedResult
      )
    })
  })
})

describe('formatTooltipValue (formatWithUnits = false)', () => {
  const testsParams = [
    {
      description: 'returns 3 if input is average speed',
      inputDisplayedData: datasetKeys[0], // 'average_speed'
      inputValue: 30,
      expectedResult: '30.00 km/h',
    },
    {
      description: 'returns 3 if input is workouts count',
      inputDisplayedData: datasetKeys[1], // 'nb_workouts'
      inputValue: 30,
      expectedResult: '30',
    },
    {
      description: 'returns 00:03 if input is total duration',
      inputDisplayedData: datasetKeys[2], // 'total_duration'
      inputValue: 30,
      expectedResult: '00:30',
    },
    {
      description: 'returns 3.00 km if input is total distance',
      inputDisplayedData: datasetKeys[3], // 'total_distance'
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 30 m if input is total ascent',
      inputDisplayedData: datasetKeys[4], // 'total_ascent'
      inputValue: 30,
      expectedResult: '30 m',
    },
    {
      description: 'returns 30 m if input is total descent',
      inputDisplayedData: datasetKeys[5], // 'total_decent'
      inputValue: 30,
      expectedResult: '30 m',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.equal(
        formatTooltipValue(
          testParams.inputDisplayedData,
          testParams.inputValue,
          false,
          false
        ),
        testParams.expectedResult
      )
    })
  })
})
