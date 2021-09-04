import { assert } from 'chai'

import { datasetKeys } from '@/utils/statistics'
import { formatTooltipValue } from '@/utils/tooltip'

describe('formatTooltipValue', () => {
  const testsParams = [
    {
      description: 'returns 3 if input is workouts count',
      inputDisplayedData: datasetKeys[0], // 'nb_workouts'
      inputValue: 3,
      expectedResult: '3',
    },
    {
      description: 'returns 00m:03s if input is total duration',
      inputDisplayedData: datasetKeys[1], // 'total_duration'
      inputValue: 3,
      expectedResult: '00m 03s',
    },
    {
      description: 'returns 3.00 if input is total distance',
      inputDisplayedData: datasetKeys[2], // 'total_distance'
      inputValue: 3,
      expectedResult: '3.00 km',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.equal(
        formatTooltipValue(
          testParams.inputDisplayedData,
          testParams.inputValue
        ),
        testParams.expectedResult
      )
    })
  })
})
