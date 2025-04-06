import { describe, it, expect } from 'vitest'

import createI18n from '@/i18n'
import { formatDuration, getDuration } from '@/utils/duration'

const { t } = createI18n.global

describe('formatDuration (without days)', () => {
  const testsParams = [
    {
      description: 'returns 00:00 if 0 seconds are provided',
      inputDuration: 0,
      expectedDuration: '00:00',
    },
    {
      description: 'returns 00:01 if 1 second is provided',
      inputDuration: 1,
      expectedDuration: '00:01',
    },
    {
      description: 'returns 01:00 if 60 seconds are provided',
      inputDuration: 60,
      expectedDuration: '01:00',
    },
    {
      description: 'returns 01:00 if 83.96767 seconds are provided',
      inputDuration: 83.96767,
      expectedDuration: '01:23',
    },
    {
      description: 'returns 20:34 if 1234 seconds are provided',
      inputDuration: 1234,
      expectedDuration: '20:34',
    },
    {
      description: 'returns 01:00:00 if 3600 seconds are provided',
      inputDuration: 3600,
      expectedDuration: '01:00:00',
    },
    {
      description: 'returns 02:42:45 if 9765 seconds are provided',
      inputDuration: 9765,
      expectedDuration: '02:42:45',
    },
    {
      description: 'returns 02:42:45 if 9765 seconds are provided',
      inputDuration: 97650,
      expectedDuration: '27:07:30',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(formatDuration(testParams.inputDuration)).toStrictEqual(
        testParams.expectedDuration
      )
    })
  })
})

describe('formatDuration (with units)', () => {
  const testsParams = [
    {
      description: 'returns 00m 00s if 0 seconds are provided',
      inputDuration: 0,
      expectedDuration: '00m 00s',
    },
    {
      description: 'returns 00m 01s if 1 second is provided',
      inputDuration: 1,
      expectedDuration: '00m 01s',
    },
    {
      description: 'returns 01m 00s if 60 seconds are provided',
      inputDuration: 60,
      expectedDuration: '01m 00s',
    },
    {
      description: 'returns 01:00 if 83.96767 seconds are provided',
      inputDuration: 83.96767,
      expectedDuration: '01m 23s',
    },
    {
      description: 'returns 20m 34s if 1234 seconds are provided',
      inputDuration: 1234,
      expectedDuration: '20m 34s',
    },
    {
      description: 'returns 01h 00m 00s if 3600 seconds are provided',
      inputDuration: 3600,
      expectedDuration: '01h 00m 00s',
    },
    {
      description: 'returns 02h 42m 45s if 9765 seconds are provided',
      inputDuration: 9765,
      expectedDuration: '02h 42m 45s',
    },
    {
      description: 'returns 1d 03h 07m 30s if 9765 seconds are provided',
      inputDuration: 97650,
      expectedDuration: '1d 03h 07m 30s',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        formatDuration(testParams.inputDuration, { formatWithUnits: true })
      ).toStrictEqual(testParams.expectedDuration)
    })
  })
})

describe('formatDuration (with hours)', () => {
  const testsParams = [
    {
      description: 'returns 00:00 if 0 seconds are provided',
      inputDuration: 0,
      expectedDuration: '00:00:00',
    },
    {
      description: 'returns 00:01 if 1 second is provided',
      inputDuration: 1,
      expectedDuration: '00:00:01',
    },
    {
      description: 'returns 01:00 if 60 seconds are provided',
      inputDuration: 60,
      expectedDuration: '00:01:00',
    },
    {
      description: 'returns 01:00 if 83.96767 seconds are provided',
      inputDuration: 83.96767,
      expectedDuration: '00:01:23',
    },
    {
      description: 'returns 20:34 if 1234 seconds are provided',
      inputDuration: 1234,
      expectedDuration: '00:20:34',
    },
    {
      description: 'returns 01:00:00 if 3600 seconds are provided',
      inputDuration: 3600,
      expectedDuration: '01:00:00',
    },
    {
      description: 'returns 02:42:45 if 9765 seconds are provided',
      inputDuration: 9765,
      expectedDuration: '02:42:45',
    },
    {
      description: 'returns 02:42:45 if 9765 seconds are provided',
      inputDuration: 97650,
      expectedDuration: '27:07:30',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        formatDuration(testParams.inputDuration, { withHours: true })
      ).toStrictEqual(testParams.expectedDuration)
    })
  })
})

describe('formatDuration (with units and hours)', () => {
  const testsParams = [
    {
      description: 'returns 00m 00s if 0 seconds are provided',
      inputDuration: 0,
      expectedDuration: '00h 00m 00s',
    },
    {
      description: 'returns 00m 01s if 1 second is provided',
      inputDuration: 1,
      expectedDuration: '00h 00m 01s',
    },
    {
      description: 'returns 01m 00s if 60 seconds are provided',
      inputDuration: 60,
      expectedDuration: '00h 01m 00s',
    },
    {
      description: 'returns 01:00 if 83.96767 seconds are provided',
      inputDuration: 83.96767,
      expectedDuration: '00h 01m 23s',
    },
    {
      description: 'returns 20m 34s if 1234 seconds are provided',
      inputDuration: 1234,
      expectedDuration: '00h 20m 34s',
    },
    {
      description: 'returns 01h 00m 00s if 3600 seconds are provided',
      inputDuration: 3600,
      expectedDuration: '01h 00m 00s',
    },
    {
      description: 'returns 02h 42m 45s if 9765 seconds are provided',
      inputDuration: 9765,
      expectedDuration: '02h 42m 45s',
    },
    {
      description: 'returns 1d 03h 07m 30s if 9765 seconds are provided',
      inputDuration: 97650,
      expectedDuration: '1d 03h 07m 30s',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        formatDuration(testParams.inputDuration, {
          withHours: true,
          formatWithUnits: true,
        })
      ).toStrictEqual(testParams.expectedDuration)
    })
  })
})

describe('getDuration ', () => {
  const testsParams = [
    {
      description: "returns 'O days' and '0h 00min' when '0:00:00' is provided",
      inputDuration: '0:00:00',
      expectedDuration: {
        days: '0 days,',
        duration: '0h 00min',
      },
    },
    {
      description: "returns 'O days' and '2h 05min' when '2:05:01' is provided",
      inputDuration: '2:05:01',
      expectedDuration: {
        days: '0 days,',
        duration: '2h 05min',
      },
    },
    {
      description:
        "returns '7 days' and '21h 30min' when '30:25:10' is provided",
      inputDuration: '7 days, 21:30:19',
      expectedDuration: {
        days: '7 days',
        duration: '21h 30min',
      },
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(getDuration(testParams.inputDuration, t)).toStrictEqual(
        testParams.expectedDuration
      )
    })
  })
})
