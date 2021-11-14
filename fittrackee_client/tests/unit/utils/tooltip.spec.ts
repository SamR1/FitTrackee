import { assert } from 'chai'

import { datasetKeys } from '@/utils/statistics'
import { formatTooltipValue } from '@/utils/tooltip'

describe('formatTooltipValue', () => {
  const testsParams = [
    {
      description: 'returns 3 if input is workouts count',
      inputDisplayedData: datasetKeys[0], // 'nb_workouts'
      inputValue: 30,
      expectedResult: '30',
    },
    {
      description: 'returns 00m:03s if input is total duration',
      inputDisplayedData: datasetKeys[1], // 'total_duration'
      inputValue: 30,
      expectedResult: '00m 30s',
    },
    {
      description: 'returns 3.00 km if input is total distance',
      inputDisplayedData: datasetKeys[2], // 'total_distance'
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 0.003 km if input is total ascent',
      inputDisplayedData: datasetKeys[3], // 'total_distance'
      inputValue: 30,
      expectedResult: '0.03 km',
    },
    {
      description: 'returns 0.003 km if input is total descent',
      inputDisplayedData: datasetKeys[4], // 'total_distance'
      inputValue: 30,
      expectedResult: '0.03 km',
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
      description: 'returns 30 if input is workouts count',
      inputDisplayedData: datasetKeys[0], // 'nb_workouts'
      inputValue: 30,
      expectedResult: '30',
    },
    {
      description: 'returns 00m:03s if input is total duration',
      inputDisplayedData: datasetKeys[1], // 'total_duration'
      inputValue: 30,
      expectedResult: '00m 30s',
    },
    {
      description: 'returns 30 mi if input is total distance',
      inputDisplayedData: datasetKeys[2], // 'total_distance'
      inputValue: 30,
      expectedResult: '30.00 mi',
    },
    {
      description: 'returns 0.03 mi if input is total ascent',
      inputDisplayedData: datasetKeys[3], // 'total_distance'
      inputValue: 30,
      expectedResult: '0.03 mi',
    },
    {
      description: 'returns 0.03 mi if input is total descent',
      inputDisplayedData: datasetKeys[4], // 'total_distance'
      inputValue: 30,
      expectedResult: '0.03 mi',
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
      description: 'returns 3 if input is workouts count',
      inputDisplayedData: datasetKeys[0], // 'nb_workouts'
      inputValue: 30,
      expectedResult: '30',
    },
    {
      description: 'returns 00:03 if input is total duration',
      inputDisplayedData: datasetKeys[1], // 'total_duration'
      inputValue: 30,
      expectedResult: '00:30',
    },
    {
      description: 'returns 3.00 km if input is total distance',
      inputDisplayedData: datasetKeys[2], // 'total_distance'
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 0.003 km if input is total ascent',
      inputDisplayedData: datasetKeys[3], // 'total_distance'
      inputValue: 30,
      expectedResult: '0.03 km',
    },
    {
      description: 'returns 0.003 km if input is total descent',
      inputDisplayedData: datasetKeys[4], // 'total_distance'
      inputValue: 30,
      expectedResult: '0.03 km',
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
