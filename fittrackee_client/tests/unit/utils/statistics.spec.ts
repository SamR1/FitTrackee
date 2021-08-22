import { assert } from 'chai'

import { sports } from './constants'

import {
  IStatisticsChartData,
  TStatisticsDatasets,
  TStatisticsFromApi,
} from '@/types/statistics'
import { formatStats, getDateKeys, getDatasets } from '@/utils/statistics'

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
          backgroundColor: [],
          data: [],
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: [],
          data: [],
        },
        {
          label: 'Hiking',
          backgroundColor: [],
          data: [],
        },
      ],
      total_distance: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: [],
          data: [],
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: [],
          data: [],
        },
        {
          label: 'Hiking',
          backgroundColor: [],
          data: [],
        },
      ],
      total_duration: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: [],
          data: [],
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: [],
          data: [],
        },
        {
          label: 'Hiking',
          backgroundColor: [],
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
          backgroundColor: [],
          data: [],
        },
      ],
      total_distance: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: [],
          data: [],
        },
      ],
      total_duration: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: [],
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
        nb_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: [],
            data: [null, null, null],
          },
          {
            label: 'Cycling (Transport)',
            backgroundColor: [],
            data: [null, null, null],
          },
          {
            label: 'Hiking',
            backgroundColor: [],
            data: [null, null, null],
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: [],
            data: [null, null, null],
          },
          {
            label: 'Cycling (Transport)',
            backgroundColor: [],
            data: [null, null, null],
          },
          {
            label: 'Hiking',
            backgroundColor: [],
            data: [null, null, null],
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: [],
            data: [null, null, null],
          },
          {
            label: 'Cycling (Transport)',
            backgroundColor: [],
            data: [null, null, null],
          },
          {
            label: 'Hiking',
            backgroundColor: [],
            data: [null, null, null],
          },
        ],
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
            backgroundColor: [],
            data: [null, null, null],
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: [],
            data: [null, null, null],
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: [],
            data: [null, null, null],
          },
        ],
      },
    }
    assert.deepEqual(
      formatStats(inputParams, false, sports, [2], inputStats),
      expected
    )
  })

  it('returns empty datasets if data and no displayed sport provided', () => {
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
        nb_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: [],
            data: [1, 1, null],
          },
          {
            label: 'Cycling (Transport)',
            backgroundColor: [],
            data: [null, 2, null],
          },
          {
            label: 'Hiking',
            backgroundColor: [],
            data: [null, null, 2],
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: [],
            data: [10, 15, null],
          },
          {
            label: 'Cycling (Transport)',
            backgroundColor: [],
            data: [null, 20, null],
          },
          {
            label: 'Hiking',
            backgroundColor: [],
            data: [null, null, 12],
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: [],
            data: [3000, 3500, null],
          },
          {
            label: 'Cycling (Transport)',
            backgroundColor: [],
            data: [null, 3000, null],
          },
          {
            label: 'Hiking',
            backgroundColor: [],
            data: [null, null, 5000],
          },
        ],
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
            backgroundColor: [],
            data: [1, 1, null],
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: [],
            data: [10, 15, null],
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: [],
            data: [3000, 3500, null],
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
