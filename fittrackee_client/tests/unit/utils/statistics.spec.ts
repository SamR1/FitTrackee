import { assert } from 'chai'

import { sports } from './fixtures'

import {
  IStatisticsChartData,
  TStatisticsDatasets,
  TStatisticsFromApi,
} from '@/types/statistics'
import {
  formatStats,
  getDateKeys,
  getDatasets,
  getStatsDateParams,
  updateChartParams,
} from '@/utils/statistics'

describe('getDateKeys (week starting Sunday)', () => {
  const testsParams = [
    {
      description: 'returns date keys for "week" duration',
      inputParams: {
        duration: 'week',
        start: new Date('August 01, 2021 00:00:00'),
        end: new Date('August 31, 2021 23:59:59.999'),
      },
      inputWeekStartingMonday: false,
      expected: [
        'August 1, 2021 00:00:00',
        'August 8, 2021 00:00:00',
        'August 15, 2021 00:00:00',
        'August 22, 2021 00:00:00',
        'August 29, 2021 00:00:00',
      ],
    },
    {
      description: 'returns date keys for "month" duration',
      inputParams: {
        duration: 'month',
        start: new Date('September 01, 2020 00:00:00'),
        end: new Date('August 31, 2021 23:59:59.999'),
      },
      inputWeekStartingMonday: false,
      expected: [
        'September 1, 2020 00:00:00',
        'October 1, 2020 00:00:00',
        'November 1, 2020 00:00:00',
        'December 1, 2020 00:00:00',
        'January 1, 2021 00:00:00',
        'February 1, 2021 00:00:00',
        'March 1, 2021 00:00:00',
        'April 1, 2021 00:00:00',
        'May 1, 2021 00:00:00',
        'June 1, 2021 00:00:00',
        'July 1, 2021 00:00:00',
        'August 1, 2021 00:00:00',
      ],
    },
    {
      description: 'returns date keys for "month" duration',
      inputParams: {
        duration: 'year',
        start: new Date('January 1, 2012 00:00:00'),
        end: new Date('December 31, 2021 23:59:59.999'),
      },
      inputWeekStartingMonday: false,
      expected: [
        'January 1, 2012 00:00:00',
        'January 1, 2013 00:00:00',
        'January 1, 2014 00:00:00',
        'January 1, 2015 00:00:00',
        'January 1, 2016 00:00:00',
        'January 1, 2017 00:00:00',
        'January 1, 2018 00:00:00',
        'January 1, 2019 00:00:00',
        'January 1, 2020 00:00:00',
        'January 1, 2021 00:00:00',
      ],
    },
  ]

  testsParams.map((testParams) =>
    it(testParams.description, () => {
      const expected: Date[] = testParams.expected.map(
        (date_string: string) => new Date(date_string)
      )
      assert.deepEqual(getDateKeys(testParams.inputParams, false), expected)
    })
  )
})

describe('getDateKeys (week starting Monday)', () => {
  const testsParams = [
    {
      description: 'returns date keys for "week" duration',
      inputParams: {
        duration: 'week',
        start: new Date('August 01, 2021 00:00:00'),
        end: new Date('August 31, 2021 23:59:59.999'),
      },
      inputWeekStartingMonday: false,
      expected: [
        'July 26, 2021 00:00:00',
        'August 2, 2021 00:00:00',
        'August 9, 2021 00:00:00',
        'August 16, 2021 00:00:00',
        'August 23, 2021 00:00:00',
        'August 30, 2021 00:00:00',
      ],
    },
    {
      description: 'returns date keys for "month" duration',
      inputParams: {
        duration: 'month',
        start: new Date('September 01, 2020 00:00:00'),
        end: new Date('August 31, 2021 23:59:59.999'),
      },
      inputWeekStartingMonday: false,
      expected: [
        'September 1, 2020 00:00:00',
        'October 1, 2020 00:00:00',
        'November 1, 2020 00:00:00',
        'December 1, 2020 00:00:00',
        'January 1, 2021 00:00:00',
        'February 1, 2021 00:00:00',
        'March 1, 2021 00:00:00',
        'April 1, 2021 00:00:00',
        'May 1, 2021 00:00:00',
        'June 1, 2021 00:00:00',
        'July 1, 2021 00:00:00',
        'August 1, 2021 00:00:00',
      ],
    },
    {
      description: 'returns date keys for "month" duration',
      inputParams: {
        duration: 'year',
        start: new Date('January 1, 2012 00:00:00'),
        end: new Date('December 31, 2021 23:59:59.999'),
      },
      inputWeekStartingMonday: false,
      expected: [
        'January 1, 2012 00:00:00',
        'January 1, 2013 00:00:00',
        'January 1, 2014 00:00:00',
        'January 1, 2015 00:00:00',
        'January 1, 2016 00:00:00',
        'January 1, 2017 00:00:00',
        'January 1, 2018 00:00:00',
        'January 1, 2019 00:00:00',
        'January 1, 2020 00:00:00',
        'January 1, 2021 00:00:00',
      ],
    },
  ]

  testsParams.map((testParams) =>
    it(testParams.description, () => {
      const expected: Date[] = testParams.expected.map(
        (date_string: string) => new Date(date_string)
      )
      assert.deepEqual(getDateKeys(testParams.inputParams, true), expected)
    })
  )
})

describe('getDatasets', () => {
  it('returns chart datasets (when no displayed data provided)', () => {
    const expected: TStatisticsDatasets = {
      nb_workouts: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          data: [],
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#88af98'],
          data: [],
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          data: [],
        },
      ],
      total_distance: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          data: [],
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#88af98'],
          data: [],
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          data: [],
        },
      ],
      total_duration: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          data: [],
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#88af98'],
          data: [],
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          data: [],
        },
      ],
    }
    assert.deepEqual(getDatasets(sports), expected)
  })
  it('returns chart datasets with only displayed sports', () => {
    const expected: TStatisticsDatasets = {
      nb_workouts: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#88af98'],
          data: [],
        },
      ],
      total_distance: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#88af98'],
          data: [],
        },
      ],
      total_duration: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#88af98'],
          data: [],
        },
      ],
    }
    assert.deepEqual(getDatasets([sports[1]]), expected)
  })
})

describe('formatStats', () => {
  it('returns empty datasets if no data and no displayed sport provided', () => {
    const inputStats: TStatisticsFromApi = {}
    const inputParams = {
      duration: 'month',
      start: new Date('May 1, 2021 00:00:00'),
      end: new Date('July 31, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['2021-05', '2021-06', '2021-07'],
      datasets: {
        nb_workouts: [],
        total_distance: [],
        total_duration: [],
      },
    }
    assert.deepEqual(
      formatStats(inputParams, false, sports, [], inputStats),
      expected
    )
  })

  it('returns empty datasets if no data and displayed sport provided', () => {
    const inputStats: TStatisticsFromApi = {}
    const inputParams = {
      duration: 'month',
      start: new Date('May 1, 2021 00:00:00'),
      end: new Date('July 31, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['2021-05', '2021-06', '2021-07'],
      datasets: {
        nb_workouts: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#88af98'],
            data: [0, 0, 0],
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#88af98'],
            data: [0, 0, 0],
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#88af98'],
            data: [0, 0, 0],
          },
        ],
      },
    }
    assert.deepEqual(
      formatStats(inputParams, false, sports, [2], inputStats),
      expected
    )
  })

  it('returns empty datasets if data provided but no displayed sport', () => {
    const inputStats: TStatisticsFromApi = {
      '2021-05': {
        1: {
          nb_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
        },
      },
      '2021-06': {
        1: {
          nb_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
        },
        2: {
          nb_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
        },
      },
      '2021-07': {
        3: {
          nb_workouts: 2,
          total_distance: 12,
          total_duration: 5000,
        },
      },
    }
    const inputParams = {
      duration: 'month',
      start: new Date('May 1, 2021 00:00:00'),
      end: new Date('July 31, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['2021-05', '2021-06', '2021-07'],
      datasets: {
        nb_workouts: [],
        total_distance: [],
        total_duration: [],
      },
    }
    assert.deepEqual(
      formatStats(inputParams, false, sports, [], inputStats),
      expected
    )
  })

  it('returns empty datasets if data and displayed sport provided', () => {
    const inputStats: TStatisticsFromApi = {
      '2021-05': {
        1: {
          nb_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
        },
      },
      '2021-06': {
        1: {
          nb_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
        },
        2: {
          nb_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
        },
      },
      '2021-07': {
        3: {
          nb_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
        },
      },
    }
    const inputParams = {
      duration: 'month',
      start: new Date('May 1, 2021 00:00:00'),
      end: new Date('July 31, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['2021-05', '2021-06', '2021-07'],
      datasets: {
        nb_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [1, 1, 0],
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [10, 15, 0],
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [3000, 3500, 0],
          },
        ],
      },
    }
    assert.deepEqual(
      formatStats(inputParams, false, sports, [1], inputStats),
      expected
    )
  })
})

describe("getStatsDateParams when time frame is 'month')", () => {
  const weekStartingMonday = [false, true]

  weekStartingMonday.map((weekStartingMonday) => {
    const testsParams = [
      {
        description: 'it returns date params when input date is 04/10/2021',
        input: {
          date: new Date('October 04, 2021 11:00:00'),
        },
        expected: {
          duration: 'month',
          start: new Date('November 01, 2020 00:00:00'),
          end: new Date('October 31, 2021 23:59:59.999'),
        },
      },
      {
        description: 'it returns date params when input date is 03/02/2020',
        input: {
          date: new Date('February 03, 2020 23:30:00'),
        },
        expected: {
          duration: 'month',
          start: new Date('March 01, 2019 00:00:00'),
          end: new Date('February 29, 2020 23:59:59.999'),
        },
      },
    ]

    testsParams.map((testParams) => {
      it(testParams.description, () => {
        assert.deepEqual(
          getStatsDateParams(
            testParams.input.date,
            'month',
            weekStartingMonday
          ),
          testParams.expected
        )
      })
    })
  })
})

describe("getStatsDateParams when time frame is 'year')", () => {
  const weekStartingMonday = [false, true]

  weekStartingMonday.map((weekStartingMonday) => {
    const testsParams = [
      {
        description: 'it returns date params when input date is 04/10/2021',
        input: {
          date: new Date('October 04, 2021 11:00:00'),
        },
        expected: {
          duration: 'year',
          start: new Date('January 01, 2012 00:00:00'),
          end: new Date('December 31, 2021 23:59:59.999'),
        },
      },
      {
        description: 'it returns date params when input date is 03/02/2020',
        input: {
          date: new Date('February 03, 2020 23:30:00'),
        },
        expected: {
          duration: 'year',
          start: new Date('January 01, 2011 00:00:00'),
          end: new Date('December 31, 2020 23:59:59.999'),
        },
      },
    ]

    testsParams.map((testParams) => {
      it(testParams.description, () => {
        assert.deepEqual(
          getStatsDateParams(testParams.input.date, 'year', weekStartingMonday),
          testParams.expected
        )
      })
    })
  })
})

describe("getStatsDateParams when time frame is 'week')", () => {
  const testsParams = [
    {
      description:
        'it returns date params when input date is 04/10/2021, when week start on Sunday',
      input: {
        date: new Date('October 04, 2021 11:00:00'),
        weekStartingMonday: false,
      },
      expected: {
        duration: 'week',
        start: new Date('August 01, 2021 00:00:00'),
        end: new Date('October 09, 2021 23:59:59.999'),
      },
    },
    {
      description:
        'it returns date params when input date is 03/02/2020, when week start on Sunday',
      input: {
        date: new Date('February 03, 2020 23:30:00'),
        weekStartingMonday: false,
      },
      expected: {
        duration: 'week',
        start: new Date('December 01, 2019 00:00:00'),
        end: new Date('February 08, 2020 23:59:59.999'),
      },
    },

    {
      description:
        'it returns date params when input date is 04/10/2021, when week start on Monday',
      input: {
        date: new Date('October 04, 2021 11:00:00'),
        weekStartingMonday: true,
      },
      expected: {
        duration: 'week',
        start: new Date('August 02, 2021 00:00:00'),
        end: new Date('October 10, 2021 23:59:59.999'),
      },
    },
    {
      description:
        'it returns date params when input date is 03/02/2020, when week start on Monday',
      input: {
        date: new Date('February 03, 2020 23:30:00'),
        weekStartingMonday: true,
      },
      expected: {
        duration: 'week',
        start: new Date('December 02, 2019 00:00:00'),
        end: new Date('February 09, 2020 23:59:59.999'),
      },
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.deepEqual(
        getStatsDateParams(
          testParams.input.date,
          'week',
          testParams.input.weekStartingMonday
        ),
        testParams.expected
      )
    })
  })
})

describe("updateChartParams when time frame is 'month')", () => {
  const weekStartingMonday = [false, true]

  weekStartingMonday.map((weekStartingMonday) => {
    const testsParams = [
      {
        description:
          'it return forward date params when start date is 01/11/2020',
        input: {
          chartParams: {
            duration: 'month',
            start: new Date('November 01, 2020 00:00:00'),
            end: new Date('October 31, 2021 23:59:59.999'),
          },
          backward: false,
        },
        expected: {
          duration: 'month',
          start: new Date('December 01, 2020 00:00:00'),
          end: new Date('November 30, 2021 23:59:59.999'),
        },
      },
      {
        description:
          'it return forward date params when start date is 01/02/2019',
        input: {
          chartParams: {
            duration: 'month',
            start: new Date('February 01, 2019 00:00:00'),
            end: new Date('January 31, 2020 23:59:59.999'),
          },
          backward: false,
        },
        expected: {
          duration: 'month',
          start: new Date('March 01, 2019 00:00:00'),
          end: new Date('February 29, 2020 23:59:59.999'),
        },
      },
      {
        description:
          'it return backward date params when input date is 01/12/2020',
        input: {
          chartParams: {
            duration: 'month',
            start: new Date('December 01, 2020 00:00:00'),
            end: new Date('November 30, 2021 23:59:59.999'),
          },
          backward: true,
        },
        expected: {
          duration: 'month',
          start: new Date('November 01, 2020 00:00:00'),
          end: new Date('October 31, 2021 23:59:59.999'),
        },
      },
      {
        description:
          'it return backward date params when input date is 01/03/2019',
        input: {
          chartParams: {
            duration: 'month',
            start: new Date('March 01, 2019 00:00:00'),
            end: new Date('February 29, 2020 23:59:59.999'),
          },
          backward: true,
        },
        expected: {
          duration: 'month',
          start: new Date('February 01, 2019 00:00:00'),
          end: new Date('January 31, 2020 23:59:59.999'),
        },
      },
    ]

    testsParams.map((testParams) => {
      it(testParams.description, () => {
        assert.deepEqual(
          updateChartParams(
            testParams.input.chartParams,
            testParams.input.backward,
            weekStartingMonday
          ),
          testParams.expected
        )
      })
    })
  })
})

describe("updateChartParams when time frame is 'year')", () => {
  const weekStartingMonday = [false, true]

  weekStartingMonday.map((weekStartingMonday) => {
    const testsParams = [
      {
        description: 'it returns date params when start date is 01/10/2012',
        input: {
          chartParams: {
            duration: 'year',
            start: new Date('January 01, 2012 00:00:00'),
            end: new Date('December 31, 2021 23:59:59.999'),
          },
          backward: false,
        },
        expected: {
          duration: 'year',
          start: new Date('January 01, 2013 00:00:00'),
          end: new Date('December 31, 2022 23:59:59.999'),
        },
      },
      {
        description: 'it returns date params when input date is 01/01/2011',
        input: {
          chartParams: {
            duration: 'year',
            start: new Date('January 01, 2011 00:00:00'),
            end: new Date('December 31, 2020 23:59:59.999'),
          },
          backward: false,
        },
        expected: {
          duration: 'year',
          start: new Date('January 01, 2012 00:00:00'),
          end: new Date('December 31, 2021 23:59:59.999'),
        },
      },
      {
        description: 'it returns date params when start date is 01/10/2013',
        input: {
          chartParams: {
            duration: 'year',
            start: new Date('January 01, 2013 00:00:00'),
            end: new Date('December 31, 2022 23:59:59.999'),
          },
          backward: true,
        },
        expected: {
          duration: 'year',
          start: new Date('January 01, 2012 00:00:00'),
          end: new Date('December 31, 2021 23:59:59.999'),
        },
      },
      {
        description: 'it returns date params when input date is 01/01/2012',
        input: {
          chartParams: {
            duration: 'year',
            start: new Date('January 01, 2012 00:00:00'),
            end: new Date('December 31, 2021 23:59:59.999'),
          },
          backward: true,
        },
        expected: {
          duration: 'year',
          start: new Date('January 01, 2011 00:00:00'),
          end: new Date('December 31, 2020 23:59:59.999'),
        },
      },
    ]

    testsParams.map((testParams) => {
      it(testParams.description, () => {
        assert.deepEqual(
          updateChartParams(
            testParams.input.chartParams,
            testParams.input.backward,
            weekStartingMonday
          ),
          testParams.expected
        )
      })
    })
  })
})

describe("updateChartParams when time frame is 'week')", () => {
  const testsParams = [
    {
      description:
        'it returns forward date params when start date is 01/09/2021 and week starts on Sunday',
      input: {
        chartParams: {
          duration: 'week',
          start: new Date('August 01, 2021 00:00:00'),
          end: new Date('October 09, 2021 23:59:59.999'),
        },
        backward: false,
        weekStartingMonday: false,
      },
      expected: {
        duration: 'week',
        start: new Date('August 08, 2021 00:00:00'),
        end: new Date('October 16, 2021 23:59:59.999'),
      },
    },
    {
      description:
        'it returns backward date params when start date is 01/09/2021 and week starts on Sunday',
      input: {
        chartParams: {
          duration: 'week',
          start: new Date('August 01, 2021 00:00:00'),
          end: new Date('October 09, 2021 23:59:59.999'),
        },
        backward: true,
        weekStartingMonday: false,
      },
      expected: {
        duration: 'week',
        start: new Date('July 25, 2021 00:00:00'),
        end: new Date('October 02, 2021 23:59:59.999'),
      },
    },
    {
      description:
        'it returns forward date params when start date is 01/09/2021 and week starts on Monday',
      input: {
        chartParams: {
          duration: 'week',
          start: new Date('August 02, 2021 00:00:00'),
          end: new Date('October 10, 2021 23:59:59.999'),
        },
        backward: false,
        weekStartingMonday: true,
      },
      expected: {
        duration: 'week',
        start: new Date('August 09, 2021 00:00:00'),
        end: new Date('October 17, 2021 23:59:59.999'),
      },
    },
    {
      description:
        'it returns backward date params when start date is 01/09/2021 and week starts on Monday',
      input: {
        chartParams: {
          duration: 'week',
          start: new Date('August 02, 2021 00:00:00'),
          end: new Date('October 10, 2021 23:59:59.999'),
        },
        backward: true,
        weekStartingMonday: true,
      },
      expected: {
        duration: 'week',
        start: new Date('July 26, 2021 00:00:00'),
        end: new Date('October 03, 2021 23:59:59.999'),
      },
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.deepEqual(
        updateChartParams(
          testParams.input.chartParams,
          testParams.input.backward,
          testParams.input.weekStartingMonday
        ),
        testParams.expected
      )
    })
  })
})
