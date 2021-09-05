import { assert, expect } from 'chai'

import { getCalendarStartAndEnd, incrementDate, startDate } from '@/utils/dates'

describe('startDate (week starting Sunday)', () => {
  const testsParams = [
    {
      description: "returns start day for 'month' duration",
      inputDuration: 'month',
      inputDate: 'August 21, 2021 20:00:00',
      expectedDate: 'August 1, 2021 00:00:00',
    },
    {
      description: "returns start day for 'week' duration",
      inputDuration: 'week',
      inputDate: 'August 21, 2021 20:00:00',
      expectedDate: 'August 15, 2021 00:00:00',
    },
    {
      description: "returns start day for 'year' duration",
      inputDuration: 'year',
      inputDate: 'August 21, 2021 20:00:00',
      expectedDate: 'January 1, 2021 00:00:00',
    },
  ]

  testsParams.map((testParams) =>
    it(testParams.description, () => {
      const day: Date = new Date(testParams.inputDate)
      const expected: Date = new Date(testParams.expectedDate)
      assert.deepEqual(
        startDate(testParams.inputDuration, day, false),
        expected
      )
    })
  )
})

describe('startDate (week starting Monday)', () => {
  const testsParams = [
    {
      description: "returns start day for 'month' duration",
      inputDuration: 'month',
      inputDate: 'August 21, 2021 20:00:00',
      expectedDate: 'August 1, 2021 00:00:00',
    },
    {
      description: 'returns start day for week duration',
      inputDuration: 'week',
      inputDate: 'August 21, 2021 20:00:00',
      expectedDate: 'August 16, 2021 00:00:00',
    },
    {
      description: "returns start day for 'year' duration",
      inputDuration: 'year',
      inputDate: 'August 21, 2021 20:00:00',
      expectedDate: 'January 1, 2021 00:00:00',
    },
  ]

  testsParams.map((testParams) =>
    it(testParams.description, () => {
      const day: Date = new Date(testParams.inputDate)
      const expected: Date = new Date(testParams.expectedDate)
      assert.deepEqual(startDate(testParams.inputDuration, day, true), expected)
    })
  )
})

describe('startDate (week starting Monday)', () => {
  it('it throws an exception if duration is invalid', () => {
    const day: Date = new Date('August 21, 2021 20:00:00')
    expect(() => startDate('invalid duration', day, true)).to.throw(
      'Invalid duration, expected: "week", "month", "year", got: "invalid duration"'
    )
  })
})

describe('dateIncrement', () => {
  const testsParams = [
    {
      description: "returns incremented day for 'month' duration",
      inputDuration: 'month',
      inputDate: 'August 21, 2021 20:00:00',
      expectedDate: 'September 21, 2021 20:00:00',
    },
    {
      description: 'returns incremented day for week duration',
      inputDuration: 'week',
      inputDate: 'August 21, 2021 20:00:00',
      expectedDate: 'August 28, 2021 20:00:00',
    },
    {
      description:
        'returns incremented day for week duration (February w/ 28 days)',
      inputDuration: 'week',
      inputDate: 'February 22, 2021 20:00:00',
      expectedDate: 'March 1, 2021 20:00:00',
    },
    {
      description:
        'returns incremented day for week duration (February w/ 29 days)',
      inputDuration: 'week',
      inputDate: 'February 22, 2020 20:00:00',
      expectedDate: 'February 29, 2020 20:00:00',
    },
    {
      description: "returns incremented day for 'year' duration",
      inputDuration: 'year',
      inputDate: 'August 21, 2021 20:00:00',
      expectedDate: 'August 21, 2022 20:00:00',
    },
    {
      description: "returns incremented day for 'year' duration (February, 29)",
      inputDuration: 'year',
      inputDate: 'February 29, 2020 20:00:00',
      expectedDate: 'February 28, 2021 20:00:00',
    },
  ]

  testsParams.map((testParams) =>
    it(testParams.description, () => {
      const day: Date = new Date(testParams.inputDate)
      const expected: Date = new Date(testParams.expectedDate)
      assert.deepEqual(incrementDate(testParams.inputDuration, day), expected)
    })
  )
})

describe('dateIncrement', () => {
  it('it throws an exception if duration is invalid', () => {
    const day: Date = new Date('August 21, 2021 20:00:00')
    expect(() => incrementDate('invalid duration', day)).to.throw(
      'Invalid duration, expected: "week", "month", "year", got: "invalid duration"'
    )
  })
})

describe('getCalendarStartAndEnd', () => {
  const testsParams = [
    {
      description: 'returns empty string if no date provided',
      inputDate: 'September 5, 2021 20:00:00',
      expectedStartDate: 'August 29, 2021 00:00:00',
      expectedEndDate: 'October 2, 2021 23:59:59.999',
    },
  ]

  testsParams.map((testParams) =>
    it(testParams.description, () => {
      const date: Date = new Date(testParams.inputDate)
      const results = getCalendarStartAndEnd(date, false)
      assert.deepEqual(results.start, new Date(testParams.expectedStartDate))
      assert.deepEqual(results.end, new Date(testParams.expectedEndDate))
    })
  )
})
