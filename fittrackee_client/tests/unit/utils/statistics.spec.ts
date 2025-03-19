import { describe, it, expect } from 'vitest'

import { IChartDataset } from '../../../src/types/chart'

import { sports } from './fixtures'

import createI18n from '@/i18n'
import {
  IStatisticsChartData,
  IStatisticsWorkoutsAverageChartData,
  TStatisticsDatasets,
  TStatisticsFromApi,
} from '@/types/statistics'
import {
  formatDateLabel,
  formatStats,
  getDateKeys,
  getDatasets,
  getStatsDateParams,
  updateChartParams,
  getWorkoutsAverageDatasets,
} from '@/utils/statistics'

const { locale, t } = createI18n.global

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
      expect(getDateKeys(testParams.inputParams, false)).toStrictEqual(expected)
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
      expect(getDateKeys(testParams.inputParams, true)).toStrictEqual(expected)
    })
  )
})

describe('getDatasets', () => {
  it('returns chart datasets (when no displayed data provided)', () => {
    const expected: TStatisticsDatasets = {
      average_distance: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          borderColor: ['#4c9792'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          borderColor: ['#000000'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          borderColor: ['#bb757c'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
      ],
      average_duration: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          borderColor: ['#4c9792'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          borderColor: ['#000000'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          borderColor: ['#bb757c'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
      ],
      average_ascent: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          borderColor: ['#4c9792'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          borderColor: ['#000000'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          borderColor: ['#bb757c'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
      ],
      average_descent: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          borderColor: ['#4c9792'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          borderColor: ['#000000'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          borderColor: ['#bb757c'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
      ],
      average_speed: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          borderColor: ['#4c9792'],
          data: [],
          type: 'line',
          spanGaps: true,
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          borderColor: ['#000000'],
          data: [],
          type: 'line',
          spanGaps: true,
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          borderColor: ['#bb757c'],
          data: [],
          type: 'line',
          spanGaps: true,
        },
      ],
      average_workouts: [],
      total_workouts: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          data: [],
          type: 'bar',
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          data: [],
          type: 'bar',
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          data: [],
          type: 'bar',
        },
      ],
      total_distance: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          data: [],
          type: 'bar',
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          data: [],
          type: 'bar',
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          data: [],
          type: 'bar',
        },
      ],
      total_duration: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          data: [],
          type: 'bar',
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          data: [],
          type: 'bar',
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          data: [],
          type: 'bar',
        },
      ],
      total_ascent: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          data: [],
          type: 'bar',
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          data: [],
          type: 'bar',
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          data: [],
          type: 'bar',
        },
      ],
      total_descent: [
        {
          label: 'Cycling (Sport)',
          backgroundColor: ['#4c9792'],
          data: [],
          type: 'bar',
        },
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          data: [],
          type: 'bar',
        },
        {
          label: 'Hiking',
          backgroundColor: ['#bb757c'],
          data: [],
          type: 'bar',
        },
      ],
    }
    expect(getDatasets(sports)).toStrictEqual(expected)
  })

  it('returns chart datasets with only displayed sports', () => {
    const expected: TStatisticsDatasets = {
      average_distance: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          borderColor: ['#000000'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
      ],
      average_duration: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          borderColor: ['#000000'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
      ],
      average_ascent: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          borderColor: ['#000000'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
      ],
      average_descent: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          borderColor: ['#000000'],
          data: [],
          spanGaps: true,
          type: 'line',
        },
      ],
      average_speed: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          borderColor: ['#000000'],
          data: [],
          type: 'line',
          spanGaps: true,
        },
      ],
      average_workouts: [],
      total_workouts: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          data: [],
          type: 'bar',
        },
      ],
      total_distance: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          data: [],
          type: 'bar',
        },
      ],
      total_duration: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          data: [],
          type: 'bar',
        },
      ],
      total_ascent: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          data: [],
          type: 'bar',
        },
      ],
      total_descent: [
        {
          label: 'Cycling (Transport)',
          backgroundColor: ['#000000'],
          data: [],
          type: 'bar',
        },
      ],
    }
    expect(getDatasets([sports[1]])).toStrictEqual(expected)
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
      labels: ['05/2021', '06/2021', '07/2021'],
      datasets: {
        average_ascent: [],
        average_descent: [],
        average_distance: [],
        average_duration: [],
        average_speed: [],
        average_workouts: [],
        total_workouts: [],
        total_distance: [],
        total_duration: [],
        total_ascent: [],
        total_descent: [],
      },
    }
    expect(
      formatStats(
        inputParams,
        false,
        sports,
        [],
        inputStats,
        false,
        'MM/dd/yyyy'
      )
    ).toStrictEqual(expected)
  })

  it('returns empty datasets if no data and displayed sport provided', () => {
    const inputStats: TStatisticsFromApi = {}
    const inputParams = {
      duration: 'month',
      start: new Date('May 1, 2021 00:00:00'),
      end: new Date('July 31, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['05/2021', '06/2021', '07/2021'],
      datasets: {
        average_distance: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#000000'],
            borderColor: ['#000000'],
            data: [null, null, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_duration: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#000000'],
            borderColor: ['#000000'],
            data: [null, null, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_ascent: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#000000'],
            borderColor: ['#000000'],
            data: [null, null, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_descent: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#000000'],
            borderColor: ['#000000'],
            data: [null, null, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_speed: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#000000'],
            borderColor: ['#000000'],
            data: [null, null, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_workouts: [],
        total_workouts: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#000000'],
            data: [0, 0, 0],
            type: 'bar',
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#000000'],
            data: [0, 0, 0],
            type: 'bar',
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#000000'],
            data: [0, 0, 0],
            type: 'bar',
          },
        ],
        total_ascent: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#000000'],
            data: [0, 0, 0],
            type: 'bar',
          },
        ],
        total_descent: [
          {
            label: 'Cycling (Transport)',
            backgroundColor: ['#000000'],
            data: [0, 0, 0],
            type: 'bar',
          },
        ],
      },
    }
    expect(
      formatStats(
        inputParams,
        false,
        sports,
        [2],
        inputStats,
        false,
        'MM/dd/yyyy'
      )
    ).toStrictEqual(expected)
  })

  it('returns empty datasets if data provided but no displayed sport', () => {
    const inputStats: TStatisticsFromApi = {
      '2021-05': {
        1: {
          average_ascent: 150,
          average_descent: 100,
          average_distance: 10,
          average_duration: 3000,
          average_speed: 12,
          total_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 100,
        },
      },
      '2021-06': {
        1: {
          average_ascent: 250,
          average_descent: 150,
          average_distance: 15,
          average_duration: 3500,
          average_speed: 18,
          total_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
          total_ascent: 250,
          total_descent: 150,
        },
        2: {
          average_ascent: 75,
          average_descent: 100,
          average_distance: 10,
          average_duration: 1500,
          average_speed: 24,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 200,
        },
      },
      '2021-07': {
        3: {
          average_distance: 6,
          average_duration: 2500,
          average_ascent: 50,
          average_descent: 50,
          average_speed: 8.64,
          total_workouts: 2,
          total_distance: 12,
          total_duration: 5000,
          total_ascent: 100,
          total_descent: 100,
        },
      },
    }
    const inputParams = {
      duration: 'month',
      start: new Date('May 1, 2021 00:00:00'),
      end: new Date('July 31, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['05/2021', '06/2021', '07/2021'],
      datasets: {
        average_ascent: [],
        average_descent: [],
        average_distance: [],
        average_duration: [],
        average_speed: [],
        average_workouts: [],
        total_workouts: [],
        total_distance: [],
        total_duration: [],
        total_ascent: [],
        total_descent: [],
      },
    }
    expect(
      formatStats(
        inputParams,
        false,
        sports,
        [],
        inputStats,
        false,
        'MM/dd/yyyy'
      )
    ).toStrictEqual(expected)
  })

  it('returns datasets when data and displayed sport provided', () => {
    const inputStats: TStatisticsFromApi = {
      '2021-05': {
        1: {
          average_ascent: 150,
          average_descent: 100,
          average_distance: 10,
          average_duration: 3000,
          average_speed: 12,
          total_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 100,
        },
      },
      '2021-06': {
        1: {
          average_ascent: 250,
          average_descent: 150,
          average_distance: 15,
          average_duration: 3500,
          average_speed: 18,
          total_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
          total_ascent: 250,
          total_descent: 150,
        },
        2: {
          average_ascent: 75,
          average_descent: 100,
          average_distance: 10,
          average_duration: 1500,
          average_speed: 24,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 200,
        },
      },
      '2021-07': {
        3: {
          average_distance: 6,
          average_duration: 2500,
          average_ascent: 50,
          average_descent: 50,
          average_speed: 8.64,
          nb_workouts: 2,
          total_distance: 12,
          total_duration: 5000,
          total_ascent: 100,
          total_descent: 100,
        },
      },
    }
    const inputParams = {
      duration: 'month',
      start: new Date('May 1, 2021 00:00:00'),
      end: new Date('July 31, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['05/2021', '06/2021', '07/2021'],
      datasets: {
        average_ascent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [150, 250, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_descent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [100, 150, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_distance: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [10, 15, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_duration: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [3000, 3500, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_speed: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [12, 18, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_workouts: [],
        total_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [1, 1, 0],
            type: 'bar',
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [10, 15, 0],
            type: 'bar',
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [3000, 3500, 0],
            type: 'bar',
          },
        ],
        total_ascent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [150, 250, 0],
            type: 'bar',
          },
        ],
        total_descent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [100, 150, 0],
            type: 'bar',
          },
        ],
      },
    }
    expect(
      formatStats(
        inputParams,
        false,
        sports,
        [1],
        inputStats,
        false,
        'MM/dd/yyyy'
      )
    ).toStrictEqual(expected)
  })
})

describe('formatStats (duration)', () => {
  it("returns datasets when duration is 'year'", () => {
    const inputStats: TStatisticsFromApi = {
      '2020': {
        1: {
          average_ascent: 150,
          average_descent: 100,
          average_distance: 10,
          average_duration: 3000,
          average_speed: 12,
          total_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 100,
        },
      },
      '2021': {
        1: {
          average_ascent: 250,
          average_descent: 150,
          average_distance: 15,
          average_duration: 3500,
          average_speed: 18,
          total_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
          total_ascent: 250,
          total_descent: 150,
        },
        2: {
          average_ascent: 75,
          average_descent: 100,
          average_distance: 10,
          average_duration: 1500,
          average_speed: 24,
          nb_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 200,
        },
      },
      '2022': {
        3: {
          average_distance: 10,
          average_duration: 1500,
          average_ascent: 50,
          average_descent: 50,
          average_speed: 14,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 100,
          total_descent: 100,
        },
      },
    }
    const inputParams = {
      duration: 'year',
      start: new Date('January 1, 2020 00:00:00'),
      end: new Date('December 31, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['2020', '2021'],
      datasets: {
        average_ascent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [150, 250],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_descent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [100, 150],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_distance: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [10, 15],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_duration: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [3000, 3500],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_speed: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [12, 18],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_workouts: [],
        total_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [1, 1],
            type: 'bar',
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [10, 15],
            type: 'bar',
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [3000, 3500],
            type: 'bar',
          },
        ],
        total_ascent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [150, 250],
            type: 'bar',
          },
        ],
        total_descent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [100, 150],
            type: 'bar',
          },
        ],
      },
    }
    expect(
      formatStats(
        inputParams,
        false,
        sports,
        [1],
        inputStats,
        false,
        'MM/dd/yyyy'
      )
    ).toStrictEqual(expected)
  })
  it("returns datasets when duration is 'month'", () => {
    const inputStats: TStatisticsFromApi = {
      '2021-10': {
        1: {
          average_ascent: 150,
          average_descent: 100,
          average_distance: 10,
          average_duration: 3000,
          average_speed: 12,
          total_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 100,
        },
      },
      '2021-11': {
        1: {
          average_ascent: 250,
          average_descent: 150,
          average_distance: 15,
          average_duration: 3500,
          average_speed: 18,
          total_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
          total_ascent: 250,
          total_descent: 150,
        },
        2: {
          average_ascent: 75,
          average_descent: 100,
          average_distance: 10,
          average_duration: 1500,
          average_speed: 24,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 200,
        },
      },
      '2021-12': {
        3: {
          average_distance: 10,
          average_duration: 1500,
          average_ascent: 50,
          average_descent: 50,
          average_speed: 8.64,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 100,
          total_descent: 100,
        },
      },
    }
    const inputParams = {
      duration: 'month',
      start: new Date('October 1, 2021 00:00:00'),
      end: new Date('December 31, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['10/2021', '11/2021', '12/2021'],
      datasets: {
        average_ascent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [150, 250, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_descent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [100, 150, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_distance: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [10, 15, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_duration: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [3000, 3500, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_speed: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [12, 18, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_workouts: [],
        total_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [1, 1, 0],
            type: 'bar',
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [10, 15, 0],
            type: 'bar',
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [3000, 3500, 0],
            type: 'bar',
          },
        ],
        total_ascent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [150, 250, 0],
            type: 'bar',
          },
        ],
        total_descent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [100, 150, 0],
            type: 'bar',
          },
        ],
      },
    }
    expect(
      formatStats(
        inputParams,
        false,
        sports,
        [1],
        inputStats,
        false,
        'MM/dd/yyyy'
      )
    ).toStrictEqual(expected)
  })

  it("returns datasets when duration is 'week' and week starts on Sunday", () => {
    const inputStats: TStatisticsFromApi = {
      '2021-10-03': {
        1: {
          average_ascent: 150,
          average_descent: 100,
          average_distance: 10,
          average_duration: 3000,
          average_speed: 12,
          total_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 100,
        },
      },
      '2021-10-10': {
        1: {
          average_ascent: 250,
          average_descent: 150,
          average_distance: 15,
          average_duration: 3500,
          average_speed: 18,
          total_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
          total_ascent: 250,
          total_descent: 150,
        },
        2: {
          average_ascent: 75,
          average_descent: 100,
          average_distance: 10,
          average_duration: 1500,
          average_speed: 24,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 200,
        },
      },
      '2021-10-17': {
        3: {
          average_distance: 10,
          average_duration: 1500,
          average_ascent: 50,
          average_descent: 50,
          average_speed: 8.64,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 100,
          total_descent: 100,
        },
      },
    }
    const inputParams = {
      duration: 'week',
      start: new Date('October 03, 2021 00:00:00'),
      end: new Date('October 23, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['10/03/2021', '10/10/2021', '10/17/2021'],
      datasets: {
        average_ascent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [150, 250, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_descent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [100, 150, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_distance: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [10, 15, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_duration: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [3000, 3500, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_speed: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [12, 18, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_workouts: [],
        total_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [1, 1, 0],
            type: 'bar',
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [10, 15, 0],
            type: 'bar',
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [3000, 3500, 0],
            type: 'bar',
          },
        ],
        total_ascent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [150, 250, 0],
            type: 'bar',
          },
        ],
        total_descent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [100, 150, 0],
            type: 'bar',
          },
        ],
      },
    }
    expect(
      formatStats(
        inputParams,
        false,
        sports,
        [1],
        inputStats,
        false,
        'MM/dd/yyyy'
      )
    ).toStrictEqual(expected)
  })

  it("returns datasets when duration is 'week' and week starts on Monday", () => {
    const inputStats: TStatisticsFromApi = {
      '2021-10-04': {
        1: {
          average_ascent: 150,
          average_descent: 100,
          average_distance: 10,
          average_duration: 3000,
          average_speed: 12,
          total_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 100,
        },
      },
      '2021-10-11': {
        1: {
          average_ascent: 250,
          average_descent: 150,
          average_distance: 15,
          average_duration: 3500,
          average_speed: 18,
          total_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
          total_ascent: 250,
          total_descent: 150,
        },
        2: {
          average_ascent: 75,
          average_descent: 100,
          average_distance: 10,
          average_duration: 1500,
          average_speed: 24,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 200,
        },
      },
      '2021-10-18': {
        3: {
          average_distance: 10,
          average_duration: 1500,
          average_ascent: 50,
          average_descent: 50,
          average_speed: 8.64,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 100,
          total_descent: 100,
        },
      },
    }
    const inputParams = {
      duration: 'week',
      start: new Date('October 04, 2021 00:00:00'),
      end: new Date('October 24, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['10/04/2021', '10/11/2021', '10/18/2021'],
      datasets: {
        average_ascent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [150, 250, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_descent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [100, 150, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_distance: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [10, 15, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_duration: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [3000, 3500, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_speed: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [12, 18, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_workouts: [],
        total_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [1, 1, 0],
            type: 'bar',
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [10, 15, 0],
            type: 'bar',
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [3000, 3500, 0],
            type: 'bar',
          },
        ],
        total_ascent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [150, 250, 0],
            type: 'bar',
          },
        ],
        total_descent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [100, 150, 0],
            type: 'bar',
          },
        ],
      },
    }
    expect(
      formatStats(
        inputParams,
        true,
        sports,
        [1],
        inputStats,
        false,
        'MM/dd/yyyy'
      )
    ).toStrictEqual(expected)
  })

  it("returns datasets when duration is 'week' and date format 'dd/MM/yyyy'", () => {
    const inputStats: TStatisticsFromApi = {
      '2021-10-03': {
        1: {
          average_ascent: 150,
          average_descent: 100,
          average_distance: 10,
          average_duration: 3000,
          average_speed: 12,
          total_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 100,
        },
      },
      '2021-10-10': {
        1: {
          average_ascent: 250,
          average_descent: 150,
          average_distance: 15,
          average_duration: 3500,
          average_speed: 18,
          total_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
          total_ascent: 250,
          total_descent: 150,
        },
        2: {
          average_ascent: 75,
          average_descent: 100,
          average_distance: 10,
          average_duration: 1500,
          average_speed: 24,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 200,
        },
      },
      '2021-10-17': {
        3: {
          average_distance: 10,
          average_duration: 1500,
          average_ascent: 50,
          average_descent: 50,
          average_speed: 8.64,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 100,
          total_descent: 100,
        },
      },
    }
    const inputParams = {
      duration: 'week',
      start: new Date('October 03, 2021 00:00:00'),
      end: new Date('October 23, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['03/10/2021', '10/10/2021', '17/10/2021'],
      datasets: {
        average_ascent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [150, 250, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_descent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [100, 150, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_distance: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [10, 15, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_duration: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [3000, 3500, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_speed: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [12, 18, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_workouts: [],
        total_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [1, 1, 0],
            type: 'bar',
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [10, 15, 0],
            type: 'bar',
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [3000, 3500, 0],
            type: 'bar',
          },
        ],
        total_ascent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [150, 250, 0],
            type: 'bar',
          },
        ],
        total_descent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [100, 150, 0],
            type: 'bar',
          },
        ],
      },
    }
    expect(
      formatStats(
        inputParams,
        false,
        sports,
        [1],
        inputStats,
        false,
        'dd/MM/yyyy'
      )
    ).toStrictEqual(expected)
  })

  it("returns datasets when duration is 'week' and date format  is 'date_string'", () => {
    locale.value = 'fr'
    const inputStats: TStatisticsFromApi = {
      '2021-10-03': {
        1: {
          average_ascent: 150,
          average_descent: 100,
          average_distance: 10,
          average_duration: 3000,
          average_speed: 12,
          total_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 100,
        },
      },
      '2021-10-10': {
        1: {
          average_ascent: 250,
          average_descent: 150,
          average_distance: 15,
          average_duration: 3500,
          average_speed: 18,
          total_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
          total_ascent: 250,
          total_descent: 150,
        },
        2: {
          average_ascent: 75,
          average_descent: 100,
          average_distance: 10,
          average_duration: 1500,
          average_speed: 24,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 200,
        },
      },
      '2021-10-17': {
        3: {
          average_distance: 10,
          average_duration: 1500,
          average_ascent: 50,
          average_descent: 50,
          average_speed: 8.64,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 100,
          total_descent: 100,
        },
      },
    }
    const inputParams = {
      duration: 'week',
      start: new Date('October 03, 2021 00:00:00'),
      end: new Date('October 23, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['3 oct. 2021', '10 oct. 2021', '17 oct. 2021'],
      datasets: {
        average_ascent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [150, 250, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_descent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [100, 150, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_distance: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [10, 15, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_duration: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [3000, 3500, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_speed: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [12, 18, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_workouts: [],
        total_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [1, 1, 0],
            type: 'bar',
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [10, 15, 0],
            type: 'bar',
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [3000, 3500, 0],
            type: 'bar',
          },
        ],
        total_ascent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [150, 250, 0],
            type: 'bar',
          },
        ],
        total_descent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [100, 150, 0],
            type: 'bar',
          },
        ],
      },
    }
    expect(
      formatStats(
        inputParams,
        false,
        sports,
        [1],
        inputStats,
        false,
        'date_string'
      )
    ).toStrictEqual(expected)
  })

  it('returns datasets after conversion to imperial units', () => {
    const inputStats: TStatisticsFromApi = {
      '2021-10-03': {
        1: {
          average_ascent: 150,
          average_descent: 100,
          average_distance: 10,
          average_duration: 3000,
          average_speed: 12,
          total_workouts: 1,
          total_distance: 10,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 100,
        },
      },
      '2021-10-10': {
        1: {
          average_ascent: 250,
          average_descent: 150,
          average_distance: 15,
          average_duration: 3500,
          average_speed: 18,
          total_workouts: 1,
          total_distance: 15,
          total_duration: 3500,
          total_ascent: 250,
          total_descent: 150,
        },
        2: {
          average_ascent: 75,
          average_descent: 100,
          average_distance: 10,
          average_duration: 1500,
          average_speed: 24,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 150,
          total_descent: 200,
        },
      },
      '2021-10-17': {
        3: {
          average_distance: 10,
          average_duration: 1500,
          average_ascent: 50,
          average_descent: 50,
          average_speed: 8.64,
          total_workouts: 2,
          total_distance: 20,
          total_duration: 3000,
          total_ascent: 100,
          total_descent: 100,
        },
      },
    }
    const inputParams = {
      duration: 'week',
      start: new Date('October 03, 2021 00:00:00'),
      end: new Date('October 23, 2021 23:59:59.999'),
    }
    const expected: IStatisticsChartData = {
      labels: ['10/03/2021', '10/10/2021', '10/17/2021'],
      datasets: {
        average_ascent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [492.13, 820.21, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_descent: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [328.08, 492.13, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_distance: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [6.21, 9.32, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_duration: [
          {
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [3000, 3500, null],
            label: 'Cycling (Sport)',
            spanGaps: true,
            type: 'line',
          },
        ],
        average_speed: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            borderColor: ['#4c9792'],
            data: [7.46, 11.18, null],
            type: 'line',
            spanGaps: true,
          },
        ],
        average_workouts: [],
        total_workouts: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [1, 1, 0],
            type: 'bar',
          },
        ],
        total_distance: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [6.21, 9.32, 0],
            type: 'bar',
          },
        ],
        total_duration: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [3000, 3500, 0],
            type: 'bar',
          },
        ],
        total_ascent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [492.13, 820.21, 0],
            type: 'bar',
          },
        ],
        total_descent: [
          {
            label: 'Cycling (Sport)',
            backgroundColor: ['#4c9792'],
            data: [328.08, 492.13, 0],
            type: 'bar',
          },
        ],
      },
    }
    expect(
      formatStats(
        inputParams,
        false,
        sports,
        [1],
        inputStats,
        true,
        'MM/dd/yyyy'
      )
    ).toStrictEqual(expected)
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
          statsType: 'total',
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
          statsType: 'total',
        },
      },
    ]

    testsParams.map((testParams) => {
      it(testParams.description, () => {
        expect(
          getStatsDateParams(
            testParams.input.date,
            'month',
            weekStartingMonday,
            'total'
          )
        ).toStrictEqual(testParams.expected)
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
          statsType: 'average',
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
          statsType: 'average',
        },
      },
    ]

    testsParams.map((testParams) => {
      it(testParams.description, () => {
        expect(
          getStatsDateParams(
            testParams.input.date,
            'year',
            weekStartingMonday,
            'average'
          )
        ).toStrictEqual(testParams.expected)
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
        statsType: 'total',
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
        statsType: 'total',
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
        statsType: 'total',
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
        statsType: 'total',
      },
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        getStatsDateParams(
          testParams.input.date,
          'week',
          testParams.input.weekStartingMonday,
          'total'
        )
      ).toStrictEqual(testParams.expected)
    })
  })
})

describe("getStatsDateParams when time frame is 'day')", () => {
  const weekStartingMonday = [false]

  weekStartingMonday.map((weekStartingMonday) => {
    const testParams = {
      description: 'it returns date params when input date is 04/10/2021',
      input: {
        date: new Date('October 04, 2021 11:00:00'),
      },
      expected: {
        duration: 'day',
        start: new Date('September 20, 2021 00:00:00'),
        end: new Date('October 04, 2021 23:59:59.999'),
        statsType: 'average',
      },
    }

    it(testParams.description, () => {
      expect(
        getStatsDateParams(
          testParams.input.date,
          'day',
          weekStartingMonday,
          'average'
        )
      ).toStrictEqual(testParams.expected)
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

            statsType: 'total',
          },
          backward: false,
        },
        expected: {
          duration: 'month',
          start: new Date('December 01, 2020 00:00:00'),
          end: new Date('November 30, 2021 23:59:59.999'),
          statsType: 'total',
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
            statsType: 'average',
          },
          backward: false,
        },
        expected: {
          duration: 'month',
          start: new Date('March 01, 2019 00:00:00'),
          end: new Date('February 29, 2020 23:59:59.999'),
          statsType: 'average',
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
            statsType: 'total',
          },
          backward: true,
        },
        expected: {
          duration: 'month',
          start: new Date('November 01, 2020 00:00:00'),
          end: new Date('October 31, 2021 23:59:59.999'),
          statsType: 'total',
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
            statsType: 'average',
          },
          backward: true,
        },
        expected: {
          duration: 'month',
          start: new Date('February 01, 2019 00:00:00'),
          end: new Date('January 31, 2020 23:59:59.999'),
          statsType: 'average',
        },
      },
    ]

    testsParams.map((testParams) => {
      it(testParams.description, () => {
        expect(
          updateChartParams(
            testParams.input.chartParams,
            testParams.input.backward,
            weekStartingMonday
          )
        ).toStrictEqual(testParams.expected)
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
            statsType: 'total',
          },
          backward: false,
        },
        expected: {
          duration: 'year',
          start: new Date('January 01, 2013 00:00:00'),
          end: new Date('December 31, 2022 23:59:59.999'),
          statsType: 'total',
        },
      },
      {
        description: 'it returns date params when input date is 01/01/2011',
        input: {
          chartParams: {
            duration: 'year',
            start: new Date('January 01, 2011 00:00:00'),
            end: new Date('December 31, 2020 23:59:59.999'),
            statsType: 'total',
          },
          backward: false,
        },
        expected: {
          duration: 'year',
          start: new Date('January 01, 2012 00:00:00'),
          end: new Date('December 31, 2021 23:59:59.999'),
          statsType: 'total',
        },
      },
      {
        description: 'it returns date params when start date is 01/10/2013',
        input: {
          chartParams: {
            duration: 'year',
            start: new Date('January 01, 2013 00:00:00'),
            end: new Date('December 31, 2022 23:59:59.999'),
            statsType: 'total',
          },
          backward: true,
        },
        expected: {
          duration: 'year',
          start: new Date('January 01, 2012 00:00:00'),
          end: new Date('December 31, 2021 23:59:59.999'),
          statsType: 'total',
        },
      },
      {
        description: 'it returns date params when input date is 01/01/2012',
        input: {
          chartParams: {
            duration: 'year',
            start: new Date('January 01, 2012 00:00:00'),
            end: new Date('December 31, 2021 23:59:59.999'),
            statsType: 'total',
          },
          backward: true,
        },
        expected: {
          duration: 'year',
          start: new Date('January 01, 2011 00:00:00'),
          end: new Date('December 31, 2020 23:59:59.999'),
          statsType: 'total',
        },
      },
    ]

    testsParams.map((testParams) => {
      it(testParams.description, () => {
        expect(
          updateChartParams(
            testParams.input.chartParams,
            testParams.input.backward,
            weekStartingMonday
          )
        ).toStrictEqual(testParams.expected)
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
          statsType: 'total',
        },
        backward: false,
        weekStartingMonday: false,
      },
      expected: {
        duration: 'week',
        start: new Date('August 08, 2021 00:00:00'),
        end: new Date('October 16, 2021 23:59:59.999'),
        statsType: 'total',
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
          statsType: 'total',
        },
        backward: true,
        weekStartingMonday: false,
      },
      expected: {
        duration: 'week',
        start: new Date('July 25, 2021 00:00:00'),
        end: new Date('October 02, 2021 23:59:59.999'),
        statsType: 'total',
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
          statsType: 'total',
        },
        backward: false,
        weekStartingMonday: true,
      },
      expected: {
        duration: 'week',
        start: new Date('August 09, 2021 00:00:00'),
        end: new Date('October 17, 2021 23:59:59.999'),
        statsType: 'total',
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
          statsType: 'total',
        },
        backward: true,
        weekStartingMonday: true,
      },
      expected: {
        duration: 'week',
        start: new Date('July 26, 2021 00:00:00'),
        end: new Date('October 03, 2021 23:59:59.999'),
        statsType: 'total',
      },
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        updateChartParams(
          testParams.input.chartParams,
          testParams.input.backward,
          testParams.input.weekStartingMonday
        )
      ).toStrictEqual(testParams.expected)
    })
  })
})

describe("updateChartParams when time frame is 'day')", () => {
  const weekStartingMonday = [false, true]

  weekStartingMonday.map((weekStartingMonday) => {
    const testsParams = [
      {
        description:
          'it returns start date params when start date is 20/09/2021',
        input: {
          chartParams: {
            duration: 'day',
            start: new Date('September 20, 2021 00:00:00'),
            end: new Date('October 04, 2021 23:59:59.999'),
            statsType: 'total',
          },
          backward: false,
        },
        expected: {
          duration: 'day',
          start: new Date('September 21, 2021 00:00:00'),
          end: new Date('October 05, 2021 23:59:59.999'),
          statsType: 'total',
        },
      },
      {
        description:
          'it returns backwards date params when start date is 20/09/2021',
        input: {
          chartParams: {
            duration: 'day',
            start: new Date('September 20, 2021 00:00:00'),
            end: new Date('October 04, 2021 23:59:59.999'),
            statsType: 'total',
          },
          backward: true,
        },
        expected: {
          duration: 'day',
          start: new Date('September 19, 2021 00:00:00'),
          end: new Date('October 03, 2021 23:59:59.999'),
          statsType: 'total',
        },
      },
    ]

    testsParams.map((testParams) => {
      it(testParams.description, () => {
        expect(
          updateChartParams(
            testParams.input.chartParams,
            testParams.input.backward,
            weekStartingMonday
          )
        ).toStrictEqual(testParams.expected)
      })
    })
  })
})

describe('getWorkoutsAverageDatasets', () => {
  const inputTotalWorkouts: IChartDataset[] = [
    {
      label: 'Cycling (Sport)',
      backgroundColor: ['#4c9792'],
      data: [2, 0, 2, 0, 2, 0, 0, 2, 2, 0],
      type: 'bar',
    },
    {
      label: 'Cycling (Transport)',
      backgroundColor: ['#88af98'],
      data: [2, 0, 1, 0, 3, 4, 1, 2, 0, 1],
      type: 'bar',
    },
    {
      label: 'Hiking',
      backgroundColor: ['#bb757c'],
      data: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
      type: 'bar',
    },
    {
      label: 'Running',
      backgroundColor: ['#835b83'],
      data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      type: 'bar',
    },
  ]

  it('returns workouts average datasets when total_workouts is an empty array', () => {
    locale.value = 'en'
    const expected: IStatisticsWorkoutsAverageChartData = {
      datasets: {
        workouts_average: [
          {
            label: 'workouts_average',
            backgroundColor: [],
            data: [],
          },
        ],
      },
      labels: [],
      workoutsAverage: 0,
    }

    expect(getWorkoutsAverageDatasets([], t)).toStrictEqual(expected)
  })
  it('returns workouts average datasets when total_workouts is not empty', () => {
    locale.value = 'en'
    const expected: IStatisticsWorkoutsAverageChartData = {
      labels: ['Cycling (Sport)', 'Cycling (Transport)', 'Hiking', 'Running'],
      datasets: {
        workouts_average: [
          {
            label: 'workouts_average',
            backgroundColor: ['#4c9792', '#88af98', '#bb757c', '#835b83'],
            data: [1, 1.4, 1, 0],
          },
        ],
      },
      workoutsAverage: 3.4,
    }

    expect(getWorkoutsAverageDatasets(inputTotalWorkouts, t)).toStrictEqual(
      expected
    )
  })
  it('returns workouts average datasets with translated labels', () => {
    locale.value = 'fr'
    const expected: IStatisticsWorkoutsAverageChartData = {
      labels: ['Course', 'Randonnée', 'Vélo (Sport)', 'Vélo (Transport)'],
      datasets: {
        workouts_average: [
          {
            label: 'workouts_average',
            backgroundColor: ['#835b83', '#bb757c', '#4c9792', '#88af98'],
            data: [0, 1, 1, 1.4],
          },
        ],
      },
      workoutsAverage: 3.4,
    }

    expect(getWorkoutsAverageDatasets(inputTotalWorkouts, t)).toStrictEqual(
      expected
    )
  })
})

describe('formatDateLabel', () => {
  const inputDate = new Date('March 19, 2025 10:00:00')
  const inputData = [
    {
      duration: 'day',
      userDateFormat: 'dd/MM/yyyy',
      dateFormat: 'MM/dd/yyyy',
      expectedDate: '19/03/2025',
    },
    {
      duration: 'week',
      userDateFormat: 'dd/MM/yyyy',
      dateFormat: 'MM/dd/yyyy',
      expectedDate: '19/03/2025',
    },
    {
      duration: 'month',
      userDateFormat: 'dd/MM/yyyy',
      dateFormat: 'MM/yyyy',
      expectedDate: '03/2025',
    },
    {
      duration: 'month',
      userDateFormat: 'dd/MM/yyyy',
      dateFormat: 'yyyy',
      expectedDate: '2025',
    },
  ]

  inputData.forEach((data) => {
    it(`returns date label for statistics for date '${inputDate}', duration '${data.duration}, userDateFormat '${data.userDateFormat}, dateFormat '${data.dateFormat}, '`, () => {
      expect(
        formatDateLabel(
          inputDate,
          data.duration,
          data.userDateFormat,
          data.dateFormat
        )
      ).toStrictEqual(data.expectedDate)
    })
  })
})
