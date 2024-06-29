import { describe, it, expect } from 'vitest'

import { formatTooltipValue } from '@/utils/tooltip'

describe('formatTooltipValue', () => {
  const testsParams = [
    {
      description: 'returns 30.00 km/h if input is average speed',
      inputDisplayedData: 'average_speed',
      inputValue: 30,
      expectedResult: '30.00 km/h',
    },
    {
      description: 'returns 30 if input is workouts count',
      inputDisplayedData: 'nb_workouts',
      inputValue: 30,
      expectedResult: '30',
    },
    {
      description: 'returns 00m:03s if input is total duration',
      inputDisplayedData: 'total_duration',
      inputValue: 30,
      expectedResult: '00m 30s',
    },
    {
      description: 'returns 30.00 km if input is total distance',
      inputDisplayedData: 'total_distance',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 30.00 km if input is total ascent',
      inputDisplayedData: 'total_ascent',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 30.00 km if input is total descent',
      inputDisplayedData: 'total_descent',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 00m 30s if input is average duration',
      inputDisplayedData: 'average_duration',
      inputValue: 30,
      expectedResult: '00m 30s',
    },
    {
      description: 'returns 30.00 km if input is average distance',
      inputDisplayedData: 'average_distance',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 30.00 km if input is average ascent',
      inputDisplayedData: 'average_ascent',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 30.00 km if input is average descent',
      inputDisplayedData: 'average_descent',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        formatTooltipValue(
          testParams.inputDisplayedData,
          testParams.inputValue,
          false
        )
      ).toStrictEqual(testParams.expectedResult)
    })
  })
})

describe('formatTooltipValue after conversion to imperial units', () => {
  const testsParams = [
    {
      description: 'returns 30.00 mi/h if input is average speed',
      inputDisplayedData: 'average_speed',
      inputValue: 30,
      expectedResult: '30.00 mi/h',
    },
    {
      description: 'returns 30 if input is workouts count',
      inputDisplayedData: 'nb_workouts',
      inputValue: 30,
      expectedResult: '30',
    },
    {
      description: 'returns 00m 30s if input is total duration',
      inputDisplayedData: 'total_duration',
      inputValue: 30,
      expectedResult: '00m 30s',
    },
    {
      description: 'returns 30 mi if input is total distance',
      inputDisplayedData: 'total_distance',
      inputValue: 30,
      expectedResult: '30.00 mi',
    },
    {
      description: 'returns 30.00 mi mi if input is total ascent',
      inputDisplayedData: 'total_ascent',
      inputValue: 30,
      expectedResult: '30.00 mi',
    },
    {
      description: 'returns 30.00 mi if input is total descent',
      inputDisplayedData: 'total_descent',
      inputValue: 30,
      expectedResult: '30.00 mi',
    },
    {
      description: 'returns 00m 30s if input is average duration',
      inputDisplayedData: 'average_duration',
      inputValue: 30,
      expectedResult: '00m 30s',
    },
    {
      description: 'returns 30 mi if input is average distance',
      inputDisplayedData: 'average_distance',
      inputValue: 30,
      expectedResult: '30.00 mi',
    },
    {
      description: 'returns 30.00 mi mi if input is average ascent',
      inputDisplayedData: 'average_ascent',
      inputValue: 30,
      expectedResult: '30.00 mi',
    },
    {
      description: 'returns 30.00 mi if input is average descent',
      inputDisplayedData: 'average_descent',
      inputValue: 30,
      expectedResult: '30.00 mi',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        formatTooltipValue(
          testParams.inputDisplayedData,
          testParams.inputValue,
          true
        )
      ).toStrictEqual(testParams.expectedResult)
    })
  })
})

describe('formatTooltipValue with unitFrom', () => {
  const testsParams = [
    {
      description: 'returns 30.00 m if input is total ascent',
      inputDisplayedData: 'total_ascent',
      inputValue: 30,
      expectedResult: '30.00 m',
      useImperialUnits: false,
    },
    {
      description: 'returns 30.00 m if input is total descent',
      inputDisplayedData: 'total_descent',
      inputValue: 30,
      expectedResult: '30.00 m',
      useImperialUnits: false,
    },
    {
      description: 'returns 30 ft if input is total ascent',
      inputDisplayedData: 'total_ascent',
      inputValue: 30,
      expectedResult: '30.00 ft',
      useImperialUnits: true,
    },
    {
      description: 'returns 30.00 ft if input is total descent',
      inputDisplayedData: 'total_descent',
      inputValue: 30,
      expectedResult: '30.00 ft',
      useImperialUnits: true,
    },
    {
      description: 'returns 30.00 m if input is average ascent',
      inputDisplayedData: 'average_ascent',
      inputValue: 30,
      expectedResult: '30.00 m',
      useImperialUnits: false,
    },
    {
      description: 'returns 30.00 m if input is average descent',
      inputDisplayedData: 'average_descent',
      inputValue: 30,
      expectedResult: '30.00 m',
      useImperialUnits: false,
    },
    {
      description: 'returns 30 ft if input is average ascent',
      inputDisplayedData: 'average_ascent',
      inputValue: 30,
      expectedResult: '30.00 ft',
      useImperialUnits: true,
    },
    {
      description: 'returns 30.00 ft if input is average descent',
      inputDisplayedData: 'average_descent',
      inputValue: 30,
      expectedResult: '30.00 ft',
      useImperialUnits: true,
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        formatTooltipValue(
          testParams.inputDisplayedData,
          testParams.inputValue,
          testParams.useImperialUnits,
          true,
          'm'
        )
      ).toStrictEqual(testParams.expectedResult)
    })
  })
})

describe('formatTooltipValue (formatWithUnits = false)', () => {
  const testsParams = [
    {
      description: 'returns 30.00 km/h if input is average speed',
      inputDisplayedData: 'average_speed',
      inputValue: 30,
      expectedResult: '30.00 km/h',
    },
    {
      description: 'returns 30 if input is workouts count',
      inputDisplayedData: 'nb_workouts',
      inputValue: 30,
      expectedResult: '30',
    },
    {
      description: 'returns 00:30 if input is total duration',
      inputDisplayedData: 'total_duration',
      inputValue: 30,
      expectedResult: '00:30',
    },
    {
      description: 'returns 30.00 km if input is total distance',
      inputDisplayedData: 'total_distance',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 30.00 km if input is total ascent',
      inputDisplayedData: 'total_ascent',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 30.00 km if input is total descent',
      inputDisplayedData: 'total_descent',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 00:30 if input is average duration',
      inputDisplayedData: 'average_duration',
      inputValue: 30,
      expectedResult: '00:30',
    },
    {
      description: 'returns 30.00 km if input is average distance',
      inputDisplayedData: 'average_distance',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 30.00 km if input is average ascent',
      inputDisplayedData: 'average_ascent',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
    {
      description: 'returns 30.00 km if input is average descent',
      inputDisplayedData: 'average_descent',
      inputValue: 30,
      expectedResult: '30.00 km',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        formatTooltipValue(
          testParams.inputDisplayedData,
          testParams.inputValue,
          false,
          false
        )
      ).toStrictEqual(testParams.expectedResult)
    })
  })
})
