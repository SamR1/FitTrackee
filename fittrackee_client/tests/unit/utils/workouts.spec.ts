import { assert } from 'chai'

import createI18n from '@/i18n'
import { getDatasets } from '@/utils/workouts'

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
