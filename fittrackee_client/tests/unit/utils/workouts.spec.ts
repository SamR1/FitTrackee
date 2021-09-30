import { assert } from 'chai'

import createI18n from '@/i18n'
import { getDatasets, getDonutDatasets } from '@/utils/workouts'

const { t, locale } = createI18n.global

describe('getDatasets', () => {
  const testparams = [
    {
      description:
        'returns empty datasets when no chart data w/ french translation',
      inputParams: {
        charData: [],
        locale: 'fr',
      },
      expected: {
        distance_labels: [],
        duration_labels: [],
        datasets: {
          speed: {
            label: 'vitesse',
            backgroundColor: ['#FFFFFF'],
            borderColor: ['#8884d8'],
            borderWidth: 2,
            data: [],
            yAxisID: 'ySpeed',
          },
          elevation: {
            label: 'altitude',
            backgroundColor: ['#e5e5e5'],
            borderColor: ['#cccccc'],
            borderWidth: 1,
            fill: true,
            data: [],
            yAxisID: 'yElevation',
          },
        },
        coordinates: [],
      },
    },
    {
      description: 'returns datasets w/ english translation',
      inputParams: {
        charData: [
          {
            distance: 0,
            duration: 0,
            elevation: 83.6,
            latitude: 48.845574,
            longitude: 2.373723,
            speed: 2.89,
            time: 'Sun, 12 Sep 2021 13:29:24 GMT',
          },
          {
            distance: 0,
            duration: 1,
            elevation: 83.7,
            latitude: 48.845578,
            longitude: 2.373732,
            speed: 1.56,
            time: 'Sun, 12 Sep 2021 13:29:25 GMT',
          },
          {
            distance: 0.01,
            duration: 96,
            elevation: 84.3,
            latitude: 48.845591,
            longitude: 2.373811,
            speed: 14.73,
            time: 'Sun, 12 Sep 2021 13:31:00 GMT',
          },
        ],
        locale: 'en',
      },
      expected: {
        distance_labels: [0, 0, 0.01],
        duration_labels: [0, 1, 96],
        datasets: {
          speed: {
            label: 'speed',
            backgroundColor: ['#FFFFFF'],
            borderColor: ['#8884d8'],
            borderWidth: 2,
            data: [2.89, 1.56, 14.73],
            yAxisID: 'ySpeed',
          },
          elevation: {
            label: 'elevation',
            backgroundColor: ['#e5e5e5'],
            borderColor: ['#cccccc'],
            borderWidth: 1,
            fill: true,
            data: [83.6, 83.7, 84.3],
            yAxisID: 'yElevation',
          },
        },
        coordinates: [
          { latitude: 48.845574, longitude: 2.373723 },
          { latitude: 48.845578, longitude: 2.373732 },
          { latitude: 48.845591, longitude: 2.373811 },
        ],
      },
    },
  ]
  testparams.map((testParams) => {
    it(testParams.description, () => {
      locale.value = testParams.inputParams.locale
      assert.deepEqual(
        getDatasets(testParams.inputParams.charData, t),
        testParams.expected
      )
    })
  })
})

describe('getDonutDatasets', () => {
  const testparams = [
    {
      description: 'returns empty datasets when no workouts provided',
      input: [],
      expected: {},
    },
    {
      description: 'returns donut chart datasets w/ count and percentage',
      input: [
        {
          ascent: null,
          ave_speed: 10.0,
          bounds: [],
          creation_date: 'Sun, 14 Jul 2019 13:51:01 GMT',
          descent: null,
          distance: 10.0,
          duration: '0:17:04',
          id: 'TfJ9nHVvoyxF2B8YBmMDB8',
          map: null,
          max_alt: null,
          max_speed: 10.0,
          min_alt: null,
          modification_date: null,
          moving: '0:17:04',
          next_workout: 'kjxavSTUrJvoAh2wvCeGEF',
          notes: '',
          pauses: null,
          previous_workout: null,
          records: [],
          segments: [],
          sport_id: 2,
          title: 'Cycling (Transport)',
          user: 'admin',
          weather_end: null,
          weather_start: null,
          with_gpx: false,
          workout_date: 'Mon, 01 Jan 2018 00:00:00 GMT',
        },
        {
          ascent: null,
          ave_speed: 16,
          bounds: [],
          creation_date: 'Sun, 14 Jul 2019 18:57:14 GMT',
          descent: null,
          distance: 12,
          duration: '0:45:00',
          id: 'kjxavSTUrJvoAh2wvCeGEF',
          map: null,
          max_alt: null,
          max_speed: 16,
          min_alt: null,
          modification_date: 'Sun, 14 Jul 2019 18:57:22 GMT',
          moving: '0:45:00',
          next_workout: 'TfJ9nHVvoyxF2B8YBmMDB8',
          notes: 'workout without gpx',
          pauses: null,
          previous_workout: 'TfJ9nHVvoyxF2B8YBmMDB8',
          records: [],
          segments: [],
          sport_id: 1,
          title: 'biking on sunday morning',
          user: 'admin',
          weather_end: null,
          weather_start: null,
          with_gpx: false,
          workout_date: 'Sun, 07 Jul 2019 07:00:00 GMT',
        },
        {
          ascent: null,
          ave_speed: 5.31,
          bounds: [],
          creation_date: 'Wed, 29 Sep 2021 06:18:44 GMT',
          descent: null,
          distance: 6.3,
          duration: '1:11:10',
          id: 'eYwTr2A5L6xX52rwwrfL4A',
          map: null,
          max_alt: null,
          max_speed: 5.31,
          min_alt: null,
          modification_date: 'Wed, 29 Sep 2021 06:54:02 GMT',
          moving: '1:11:10',
          next_workout: 'oN4kVTRCdsy2cGNKANSJKM',
          notes: '',
          pauses: null,
          previous_workout: 'kjxavSTUrJvoAh2wvCeGEF',
          records: [],
          segments: [],
          sport_id: 2,
          title: 'Cycling (Transport) - 2021-09-21 21:00:00',
          user: 'admin',
          weather_end: null,
          weather_start: null,
          with_gpx: false,
          workout_date: 'Tue, 21 Sep 2021 19:00:00 GMT',
        },
        {
          ascent: null,
          ave_speed: 3.97,
          bounds: [],
          creation_date: 'Thu, 30 Sep 2021 18:55:54 GMT',
          descent: null,
          distance: 5,
          duration: '1:15:30',
          id: 'FiRvMtGJCp56dqN8qfn8BK',
          map: null,
          max_alt: null,
          max_speed: 3.97,
          min_alt: null,
          modification_date: null,
          moving: '1:15:30',
          next_workout: '2GZm7YgULHi9b4kCHDbHsY',
          notes: '',
          pauses: null,
          previous_workout: '2GZm7YgULHi9b4kCHDbHsY',
          records: [],
          segments: [],
          sport_id: 3,
          title: 'just hiking',
          user: 'admin',
          weather_end: null,
          weather_start: null,
          with_gpx: false,
          workout_date: 'Mon, 20 Sep 2021 07:00:00 GMT',
        },
      ],
      expected: {
        1: {
          count: 1,
          percentage: 0.25,
        },
        2: {
          count: 2,
          percentage: 0.5,
        },
        3: {
          count: 1,
          percentage: 0.25,
        },
      },
    },
  ]
  testparams.map((testParams) => {
    it(testParams.description, () => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      assert.deepEqual(getDonutDatasets(testParams.input), testParams.expected)
    })
  })
})
