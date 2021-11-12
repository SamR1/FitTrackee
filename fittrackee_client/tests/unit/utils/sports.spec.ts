import { assert } from 'chai'

import { sports } from './fixtures'

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
      expected: [
        {
          color: null,
          has_workouts: false,
          id: 1,
          img: '/img/sports/cycling-sport.png',
          is_active: true,
          is_active_for_user: true,
          label: 'Cycling (Sport)',
          stopped_speed_threshold: 1,
          translatedLabel: 'Cycling (Sport)',
        },
        {
          color: '#000000',
          has_workouts: false,
          id: 2,
          img: '/img/sports/cycling-transport.png',
          is_active: false,
          is_active_for_user: false,
          label: 'Cycling (Transport)',
          stopped_speed_threshold: 1,
          translatedLabel: 'Cycling (Transport)',
        },
        {
          color: null,
          has_workouts: true,
          id: 3,
          img: '/img/sports/hiking.png',
          is_active: true,
          is_active_for_user: false,
          label: 'Hiking',
          stopped_speed_threshold: 0.1,
          translatedLabel: 'Hiking',
        },
      ],
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
          color: null,
          has_workouts: false,
          id: 1,
          img: '/img/sports/cycling-sport.png',
          is_active: true,
          is_active_for_user: true,
          label: 'Cycling (Sport)',
          stopped_speed_threshold: 1,
          translatedLabel: 'Cycling (Sport)',
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
          color: null,
          has_workouts: true,
          id: 3,
          img: '/img/sports/hiking.png',
          is_active: true,
          is_active_for_user: false,
          label: 'Hiking',
          stopped_speed_threshold: 0.1,
          translatedLabel: 'Randonnée',
        },
        {
          color: null,
          has_workouts: false,
          id: 1,
          img: '/img/sports/cycling-sport.png',
          is_active: true,
          is_active_for_user: true,
          label: 'Cycling (Sport)',
          stopped_speed_threshold: 1,
          translatedLabel: 'Vélo (Sport)',
        },
        {
          color: '#000000',
          has_workouts: false,
          id: 2,
          img: '/img/sports/cycling-transport.png',
          is_active: false,
          is_active_for_user: false,
          label: 'Cycling (Transport)',
          stopped_speed_threshold: 1,
          translatedLabel: 'Vélo (Transport)',
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
          color: null,
          has_workouts: false,
          id: 1,
          img: '/img/sports/cycling-sport.png',
          is_active: true,
          is_active_for_user: true,
          label: 'Cycling (Sport)',
          stopped_speed_threshold: 1,
          translatedLabel: 'Vélo (Sport)',
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
