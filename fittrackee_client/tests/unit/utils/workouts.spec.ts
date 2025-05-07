import { describe, it, expect } from 'vitest'

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
        useImperialUnits: false,
      },
      expected: {
        distance_labels: [],
        duration_labels: [],
        datasets: {
          speed: {
            id: 'speed',
            label: 'vitesse',
            backgroundColor: ['transparent'],
            borderColor: ['#8884d8'],
            borderWidth: 2,
            data: [],
            yAxisID: 'yMultiple',
          },
          elevation: {
            id: 'elevation',
            label: 'altitude',
            backgroundColor: ['#e5e5e5'],
            borderColor: ['#cccccc'],
            borderWidth: 1,
            fill: true,
            data: [],
            yAxisID: 'yElevation',
          },
          hr: {
            id: 'hr',
            label: 'fréquence cardiaque',
            backgroundColor: ['transparent'],
            borderColor: ['#ec1f5e'],
            borderWidth: 1,
            data: [],
            yAxisID: 'yMultiple',
          },
          cadence: {
            id: 'cadence',
            label: 'cadence',
            backgroundColor: ['transparent'],
            borderColor: ['#494949'],
            borderWidth: 1,
            data: [],
            yAxisID: 'yMultiple',
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
            distance: 0.66,
            duration: 493.855,
            elevation: 95.4,
            latitude: 48.846386,
            longitude: 2.379495,
            speed: 20.64,
            time: 'Sun, 12 Sep 2021 13:37:38 GMT',
          },
          {
            distance: 1.25,
            duration: 637.864,
            elevation: 91.1,
            latitude: 48.84733,
            longitude: 2.387452,
            speed: 13.03,
            time: 'Sun, 12 Sep 2021 13:40:02 GMT',
          },
        ],
        locale: 'en',
        useImperialUnits: false,
      },
      expected: {
        distance_labels: [0, 0.66, 1.25],
        duration_labels: [0, 493.855, 637.864],
        datasets: {
          speed: {
            id: 'speed',
            label: 'speed',
            backgroundColor: ['transparent'],
            borderColor: ['#8884d8'],
            borderWidth: 2,
            data: [2.89, 20.64, 13.03],
            yAxisID: 'yMultiple',
          },
          elevation: {
            id: 'elevation',
            label: 'elevation',
            backgroundColor: ['#e5e5e5'],
            borderColor: ['#cccccc'],
            borderWidth: 1,
            fill: true,
            data: [83.6, 95.4, 91.1],
            yAxisID: 'yElevation',
          },
          hr: {
            id: 'hr',
            label: 'heart rate',
            backgroundColor: ['transparent'],
            borderColor: ['#ec1f5e'],
            borderWidth: 1,
            data: [],
            yAxisID: 'yMultiple',
          },
          cadence: {
            id: 'cadence',
            label: 'cadence',
            backgroundColor: ['transparent'],
            borderColor: ['#494949'],
            borderWidth: 1,
            data: [],
            yAxisID: 'yMultiple',
          },
        },
        coordinates: [
          { latitude: 48.845574, longitude: 2.373723 },
          { latitude: 48.846386, longitude: 2.379495 },
          { latitude: 48.84733, longitude: 2.387452 },
        ],
      },
    },
    {
      description: 'returns datasets w/ units conversion',
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
            distance: 0.66,
            duration: 493.855,
            elevation: 95.4,
            latitude: 48.846386,
            longitude: 2.379495,
            speed: 20.64,
            time: 'Sun, 12 Sep 2021 13:37:38 GMT',
          },
          {
            distance: 1.25,
            duration: 637.864,
            elevation: 91.1,
            latitude: 48.84733,
            longitude: 2.387452,
            speed: 13.03,
            time: 'Sun, 12 Sep 2021 13:40:02 GMT',
          },
        ],
        locale: 'en',
        useImperialUnits: true,
      },
      expected: {
        distance_labels: [0, 0.41, 0.78],
        duration_labels: [0, 493.855, 637.864],
        datasets: {
          speed: {
            id: 'speed',
            label: 'speed',
            backgroundColor: ['transparent'],
            borderColor: ['#8884d8'],
            borderWidth: 2,
            data: [1.8, 12.83, 8.1],
            yAxisID: 'yMultiple',
          },
          elevation: {
            id: 'elevation',
            label: 'elevation',
            backgroundColor: ['#e5e5e5'],
            borderColor: ['#cccccc'],
            borderWidth: 1,
            fill: true,
            data: [274.28, 312.99, 298.88],
            yAxisID: 'yElevation',
          },
          hr: {
            id: 'hr',
            label: 'heart rate',
            backgroundColor: ['transparent'],
            borderColor: ['#ec1f5e'],
            borderWidth: 1,
            data: [],
            yAxisID: 'yMultiple',
          },
          cadence: {
            id: 'cadence',
            label: 'cadence',
            backgroundColor: ['transparent'],
            borderColor: ['#494949'],
            borderWidth: 1,
            data: [],
            yAxisID: 'yMultiple',
          },
        },
        coordinates: [
          { latitude: 48.845574, longitude: 2.373723 },
          { latitude: 48.846386, longitude: 2.379495 },
          { latitude: 48.84733, longitude: 2.387452 },
        ],
      },
    },
  ]
  testparams.map((testParams) => {
    it(testParams.description, () => {
      locale.value = testParams.inputParams.locale
      expect(
        getDatasets(
          testParams.inputParams.charData,
          t,
          testParams.inputParams.useImperialUnits
        )
      ).toStrictEqual(testParams.expected)
    })
  })
})

describe('getDatasets with dark mode', () => {
  const testparams = [
    {
      description: 'it returns dark mode color',
      inputParams: {
        charData: [],
        locale: 'fr',
        useImperialUnits: false,
        useDarkMode: true,
      },
      expected: {
        distance_labels: [],
        duration_labels: [],
        datasets: {
          speed: {
            id: 'speed',
            label: 'vitesse',
            backgroundColor: ['transparent'],
            borderColor: ['#5f5c97'],
            borderWidth: 2,
            data: [],
            yAxisID: 'yMultiple',
          },
          elevation: {
            id: 'elevation',
            label: 'altitude',
            backgroundColor: ['#303030'],
            borderColor: ['#222222'],
            borderWidth: 1,
            fill: true,
            data: [],
            yAxisID: 'yElevation',
          },
          hr: {
            id: 'hr',
            label: 'fréquence cardiaque',
            backgroundColor: ['transparent'],
            borderColor: ['#b41e4a'],
            borderWidth: 1,
            data: [],
            yAxisID: 'yMultiple',
          },
          cadence: {
            id: 'cadence',
            label: 'cadence',
            backgroundColor: ['transparent'],
            borderColor: ['#989898'],
            borderWidth: 1,
            data: [],
            yAxisID: 'yMultiple',
          },
        },
        coordinates: [],
      },
    },
    {
      description: 'it returns light mode color',
      inputParams: {
        charData: [],
        locale: 'fr',
        useImperialUnits: false,
        useDarkMode: false,
      },
      expected: {
        distance_labels: [],
        duration_labels: [],
        datasets: {
          speed: {
            id: 'speed',
            label: 'vitesse',
            backgroundColor: ['transparent'],
            borderColor: ['#8884d8'],
            borderWidth: 2,
            data: [],
            yAxisID: 'yMultiple',
          },
          elevation: {
            id: 'elevation',
            label: 'altitude',
            backgroundColor: ['#e5e5e5'],
            borderColor: ['#cccccc'],
            borderWidth: 1,
            fill: true,
            data: [],
            yAxisID: 'yElevation',
          },
          hr: {
            id: 'hr',
            label: 'fréquence cardiaque',
            backgroundColor: ['transparent'],
            borderColor: ['#ec1f5e'],
            borderWidth: 1,
            data: [],
            yAxisID: 'yMultiple',
          },
          cadence: {
            id: 'cadence',
            label: 'cadence',
            backgroundColor: ['transparent'],
            borderColor: ['#494949'],
            borderWidth: 1,
            data: [],
            yAxisID: 'yMultiple',
          },
        },
        coordinates: [],
      },
    },
  ]
  testparams.map((testParams) => {
    it(testParams.description, () => {
      locale.value = testParams.inputParams.locale
      expect(
        getDatasets(
          testParams.inputParams.charData,
          t,
          testParams.inputParams.useImperialUnits,
          testParams.inputParams.useDarkMode
        )
      ).toStrictEqual(testParams.expected)
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
      expect(getDonutDatasets(testParams.input)).toStrictEqual(
        testParams.expected
      )
    })
  })
})
