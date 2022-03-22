import { assert } from 'chai'

import { sports } from './fixtures'

import createI18n from '@/i18n'
import { ISport, TActiveStatus } from '@/types/sports'
import { translateSports } from '@/utils/sports'

const { t, locale } = createI18n.global

interface IInputParam {
  sports: ISport[]
  locale: string
  activeStatus: TActiveStatus
  sportsToInclude: number[]
}

interface ITestParameter {
  description: string
  inputParams: IInputParam
  expected: Record<never, never>[]
}

describe('translateSports', () => {
  const testsParams: ITestParameter[] = [
    {
      description: "returns sorted all translated sports (with 'en' locale)",
      inputParams: {
        sports,
        locale: 'en',
        activeStatus: 'all',
        sportsToInclude: [],
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
        "returns sorted only active translated sports (with 'en' locales)",
      inputParams: {
        sports,
        locale: 'en',
        activeStatus: 'is_active',
        sportsToInclude: [],
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
        "returns sorted translated sports active for user (with 'en' locales)",
      inputParams: {
        sports,
        locale: 'en',
        activeStatus: 'is_active_for_user',
        sportsToInclude: [],
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
      description: "returns empty array if not sports (with 'en' locale)",
      inputParams: {
        sports: [],
        locale: 'en',
        activeStatus: 'all',
        sportsToInclude: [],
      },
      expected: [],
    },
    {
      description: "returns sorted all translated sports (with 'fr' locale)",
      inputParams: {
        sports,
        locale: 'fr',
        activeStatus: 'all',
        sportsToInclude: [],
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
        "returns sorted only active translated sports (with 'fr' locales)",
      inputParams: {
        sports,
        locale: 'fr',
        activeStatus: 'is_active',
        sportsToInclude: [],
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
      ],
    },
    {
      description:
        "returns sorted translated sports, active for user (with 'fr' locales)",
      inputParams: {
        sports,
        locale: 'fr',
        activeStatus: 'is_active_for_user',
        sportsToInclude: [],
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
      description: "returns empty array if not sports (with 'fr' locale)",
      inputParams: {
        sports: [],
        locale: 'fr',
        activeStatus: 'all',
        sportsToInclude: [],
      },
      expected: [],
    },
    {
      description:
        "returns sorted all translated sports, even with user sports list provided (with 'en' locale)",
      inputParams: {
        sports,
        locale: 'en',
        activeStatus: 'all',
        sportsToInclude: [2],
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
        activeStatus: 'is_active',
        sportsToInclude: [2],
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
        activeStatus: 'all',
        sportsToInclude: [2],
      },
      expected: [],
    },
    {
      description:
        "returns sorted all translated sports, even with user sports list provided (with 'fr' locale)",
      inputParams: {
        sports,
        locale: 'fr',
        activeStatus: 'all',
        sportsToInclude: [2],
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
        activeStatus: 'is_active',
        sportsToInclude: [2],
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
        activeStatus: 'all',
        sportsToInclude: [2],
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
          testParams.inputParams.activeStatus,
          testParams.inputParams.sportsToInclude
        ),
        testParams.expected
      )
    })
  })
})
