import { assert, expect } from 'chai'

import {
  getCalendarStartAndEnd,
  incrementDate,
  getStartDate,
  formatWorkoutDate,
  formatDate,
  availableDateFormatOptions,
  getDateFormat,
} from '@/utils/dates'

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
        getStartDate(testParams.inputDuration, day, false),
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
      assert.deepEqual(
        getStartDate(testParams.inputDuration, day, true),
        expected
      )
    })
  )
})

describe('startDate (week starting Monday)', () => {
  it('it throws an exception if duration is invalid', () => {
    const day: Date = new Date('August 21, 2021 20:00:00')
    expect(() => getStartDate('invalid duration', day, true)).to.throw(
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
      description: 'returns start and end dates for calendar',
      inputDate: 'September 5, 2021 20:00:00',
      inputWeekStartingMonday: false,
      expectedStartDate: 'August 29, 2021 00:00:00',
      expectedEndDate: 'October 2, 2021 23:59:59.999',
    },
    {
      description:
        'returns start and end dates for calendar when week starts on Monday',
      inputDate: 'April 1, 2021 20:00:00',
      inputWeekStartingMonday: true,
      expectedStartDate: 'March 29, 2021 00:00:00',
      expectedEndDate: 'May 2, 2021 23:59:59.999',
    },
  ]

  testsParams.map((testParams) =>
    it(testParams.description, () => {
      const date: Date = new Date(testParams.inputDate)
      const results = getCalendarStartAndEnd(
        date,
        testParams.inputWeekStartingMonday
      )
      assert.deepEqual(results.start, new Date(testParams.expectedStartDate))
      assert.deepEqual(results.end, new Date(testParams.expectedEndDate))
    })
  )
})

describe('formatWorkoutDate', () => {
  const testsParams = [
    {
      description: 'returns date and time with default format',
      inputParams: {
        date: new Date('August 21, 2021 20:00:00'),
        dateFormat: null,
        timeFormat: null,
      },
      expected: {
        workout_date: '2021/08/21',
        workout_time: '20:00',
      },
    },
    {
      description: 'returns date and time with provided date format',
      inputParams: {
        date: new Date('August 21, 2021 20:00:00'),
        dateFormat: 'dd MM yyyy',
        timeFormat: null,
      },
      expected: {
        workout_date: '21 08 2021',
        workout_time: '20:00',
      },
    },
    {
      description: 'returns date and time with provided time format',
      inputParams: {
        date: new Date('August 21, 2021 20:00:00'),
        dateFormat: null,
        timeFormat: 'HH:mm:ss',
      },
      expected: {
        workout_date: '2021/08/21',
        workout_time: '20:00:00',
      },
    },
    {
      description: 'returns date and time with provided date and time formats',
      inputParams: {
        date: new Date('August 21, 2021 20:00:00'),
        dateFormat: 'dd-MM-yyyy',
        timeFormat: 'HH:mm:ss',
      },
      expected: {
        workout_date: '21-08-2021',
        workout_time: '20:00:00',
      },
    },
  ]
  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.deepEqual(
        formatWorkoutDate(
          testParams.inputParams.date,
          testParams.inputParams.dateFormat,
          testParams.inputParams.timeFormat
        ),
        testParams.expected
      )
    })
  })
})

describe('formatDate', () => {
  const dateString = 'Tue, 01 Nov 2022 00:00:00 GMT'

  const testsParams = [
    {
      description:
        'format date for "Europe/Paris" timezone and "dd/MM/yyyy" format (with time)',
      inputParams: {
        timezone: 'Europe/Paris',
        dateFormat: 'dd/MM/yyyy',
        withTime: true,
      },
      expectedDate: '01/11/2022 01:00',
    },
    {
      description:
        'format date for "America/New_York" timezone and "MM/dd/yyyy" format (w/o time)',
      inputParams: {
        timezone: 'America/New_York',
        dateFormat: 'MM/dd/yyyy',
        withTime: false,
      },
      expectedDate: '10/31/2022',
    },
  ]
  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.deepEqual(
        formatDate(
          dateString,
          testParams.inputParams.timezone,
          testParams.inputParams.dateFormat,
          testParams.inputParams.withTime
        ),
        testParams.expectedDate
      )
    })
  })
})

describe('formatDate (w/ default value)', () => {
  it('format date for "Europe/Paris" timezone and "dd/MM/yyyy" format', () => {
    assert.deepEqual(
      formatDate('Tue, 01 Nov 2022 00:00:00 GMT', 'Europe/Paris', 'yyyy-MM-dd'),
      '2022-11-01 01:00'
    )
  })
})

describe('getDateFormat', () => {
  const testsParams = [
    {
      inputParams: {
        dateFormat: 'dd/MM/yyyy',
        language: 'en',
      },
      expectedFormat: 'dd/MM/yyyy',
    },
    {
      inputParams: {
        dateFormat: 'MM/dd/yyyy',
        language: 'en',
      },
      expectedFormat: 'MM/dd/yyyy',
    },
    {
      inputParams: {
        dateFormat: 'yyyy-MM-dd',
        language: 'en',
      },
      expectedFormat: 'yyyy-MM-dd',
    },
    {
      inputParams: {
        dateFormat: 'date_string',
        language: 'en',
      },
      expectedFormat: 'MMM. do, yyyy',
    },
    {
      inputParams: {
        dateFormat: 'date_string',
        language: 'fr',
      },
      expectedFormat: 'd MMM yyyy',
    },
    {
      inputParams: {
        dateFormat: 'date_string',
        language: 'de',
      },
      expectedFormat: 'do MMM yyyy',
    },
  ]
  testsParams.map((testParams) => {
    it(`get date format for "${testParams.inputParams.language}" and  "${testParams.inputParams.dateFormat}" `, () => {
      assert.deepEqual(
        getDateFormat(
          testParams.inputParams.dateFormat,
          testParams.inputParams.language
        ),
        testParams.expectedFormat
      )
    })
  })
})

describe('availableDateFormatOptions', () => {
  const inputDate = `Sun, 9 Oct 2022 18:18:41 GMT`
  const inputTimezone = `Europe/Paris`

  const testsParams = [
    {
      inputLanguage: 'en',
      expectedOptions: [
        { label: 'dd/MM/yyyy - 09/10/2022', value: 'dd/MM/yyyy' },
        { label: 'MM/dd/yyyy - 10/09/2022', value: 'MM/dd/yyyy' },
        { label: 'yyyy-MM-dd - 2022-10-09', value: 'yyyy-MM-dd' },
        { label: 'MMM. do, yyyy - Oct. 9th, 2022', value: 'date_string' },
      ],
    },
    {
      inputLanguage: 'fr',
      expectedOptions: [
        { label: 'dd/MM/yyyy - 09/10/2022', value: 'dd/MM/yyyy' },
        { label: 'MM/dd/yyyy - 10/09/2022', value: 'MM/dd/yyyy' },
        { label: 'yyyy-MM-dd - 2022-10-09', value: 'yyyy-MM-dd' },
        { label: 'd MMM yyyy - 9 oct. 2022', value: 'date_string' },
      ],
    },
    {
      inputLanguage: 'de',
      expectedOptions: [
        { label: 'dd/MM/yyyy - 09/10/2022', value: 'dd/MM/yyyy' },
        { label: 'MM/dd/yyyy - 10/09/2022', value: 'MM/dd/yyyy' },
        { label: 'yyyy-MM-dd - 2022-10-09', value: 'yyyy-MM-dd' },
        { label: 'do MMM yyyy - 9. Okt. 2022', value: 'date_string' },
      ],
    },
  ]

  testsParams.map((testParams) => {
    it(`returns available options for ${testParams.inputLanguage} locale`, () => {
      assert.deepEqual(
        availableDateFormatOptions(
          inputDate,
          inputTimezone,
          testParams.inputLanguage
        ),
        testParams.expectedOptions
      )
    })
  })
})
