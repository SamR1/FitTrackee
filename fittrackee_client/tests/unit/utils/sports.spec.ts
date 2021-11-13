import { assert } from 'chai'

import { sports } from './fixtures'

import createI18n from '@/i18n'
import { translateSports } from '@/utils/sports'

const { t, locale } = createI18n.global

describe('translateSports', () => {
  const testsParams = [
    {
      description: "returns sorted all translated sports (with 'en' locale)",
      inputParams: {
        sports,
        locale: 'en',
        onlyActive: false,
        userSports: null,
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
          has_workouts: true,
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
        "returns sorted only translated sports, active for user (with 'en' locales)",
      inputParams: {
        sports,
        locale: 'en',
        onlyActive: true,
        userSports: null,
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
        userSports: null,
      },
      expected: [],
    },
    {
      description: "returns sorted all translated sports (with 'fr' locale)",
      inputParams: {
        sports,
        locale: 'fr',
        onlyActive: false,
        userSports: [],
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
          has_workouts: true,
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
        "returns sorted only translated sports, active for user (with 'fr' locales)",
      inputParams: {
        sports,
        locale: 'fr',
        onlyActive: true,
        userSports: null,
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
        userSports: null,
      },
      expected: [],
    },
    {
      description:
        "returns sorted all translated sports, even with user sports list provided (with 'en' locale)",
      inputParams: {
        sports,
        locale: 'en',
        onlyActive: false,
        userSports: [2],
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
          has_workouts: true,
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
        "returns sorted only translated sports active on application and sports with user workouts (with 'en' locales)",
      inputParams: {
        sports,
        locale: 'en',
        onlyActive: true,
        userSports: [2],
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
          has_workouts: true,
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
        "returns empty array, with user sports list provided (with 'en' locale)",
      inputParams: {
        sports: [],
        locale: 'en',
        onlyActive: false,
        userSports: null,
      },
      expected: [],
    },
    {
      description:
        "returns sorted all translated sports, even with user sports list provided (with 'fr' locale)",
      inputParams: {
        sports,
        locale: 'fr',
        onlyActive: false,
        userSports: [2],
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
          has_workouts: true,
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
        "returns sorted only translated sports active on application and sports with user workouts (with 'fr' locales)",
      inputParams: {
        sports,
        locale: 'fr',
        onlyActive: true,
        userSports: [2],
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
          has_workouts: true,
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
        "returns empty array, with user sports list provided  (with 'fr' locale)",
      inputParams: {
        sports: [],
        locale: 'fr',
        onlyActive: false,
        userSports: [2],
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
          testParams.inputParams.onlyActive,
          testParams.inputParams.userSports
        ),
        testParams.expected
      )
    })
  })
})
