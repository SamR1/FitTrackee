import { assert } from 'chai'

import { sports } from './constants'

import createI18n from '@/i18n'
import { translateSports } from '@/utils/sports'

const { t, locale } = createI18n.global

describe('sortSports', () => {
  const testsParams = [
    {
      description: "returns sorted all translated sports (with 'en' locale)",
      inputParams: {
        sports,
        locale: 'en',
        onlyActive: false,
      },
      expected: sports,
    },
    {
      description:
        "returns sorted only active translated sports (with 'en' locales)",
      inputParams: {
        sports,
        locale: 'en',
        onlyActive: true,
      },
      expected: [
        {
          has_workouts: false,
          id: 1,
          img: '/img/sports/cycling-sport.png',
          is_active: true,
          label: 'Cycling (Sport)',
        },
        {
          has_workouts: true,
          id: 3,
          img: '/img/sports/hiking.png',
          is_active: true,
          label: 'Hiking',
        },
      ],
    },
    {
      description: "returns empty array (with 'en' locale)",
      inputParams: {
        sports: [],
        locale: 'en',
        onlyActive: false,
      },
      expected: [],
    },
    {
      description: "returns sorted all translated sports (with 'fr' locale)",
      inputParams: {
        sports,
        locale: 'fr',
        onlyActive: false,
      },
      expected: [
        {
          has_workouts: true,
          id: 3,
          img: '/img/sports/hiking.png',
          is_active: true,
          label: 'Randonnée',
        },
        {
          has_workouts: false,
          id: 1,
          img: '/img/sports/cycling-sport.png',
          is_active: true,
          label: 'Vélo (Sport)',
        },
        {
          has_workouts: false,
          id: 2,
          img: '/img/sports/cycling-transport.png',
          is_active: false,
          label: 'Vélo (Transport)',
        },
      ],
    },
    {
      description:
        "returns sorted only active translated sports (with 'fr' locales)",
      inputParams: {
        sports,
        locale: 'fr',
        onlyActive: true,
      },
      expected: [
        {
          has_workouts: true,
          id: 3,
          img: '/img/sports/hiking.png',
          is_active: true,
          label: 'Randonnée',
        },
        {
          has_workouts: false,
          id: 1,
          img: '/img/sports/cycling-sport.png',
          is_active: true,
          label: 'Vélo (Sport)',
        },
      ],
    },
    {
      description: "returns empty array (with 'fr' locale)",
      inputParams: {
        sports: [],
        locale: 'fr',
        onlyActive: false,
      },
      expected: [],
    },
  ]
  testsParams.map((testParams) => {
    it(testParams.description, () => {
      locale.value = testParams.inputParams.locale
      assert.deepEqual(
        translateSports(
          testParams.inputParams.sports,
          t,
          testParams.inputParams.onlyActive
        ),
        testParams.expected
      )
    })
  })
})
