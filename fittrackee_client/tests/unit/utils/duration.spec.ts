import { assert } from 'chai'

import { formatDuration } from '@/utils/duration'

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
      assert.equal(
        formatDuration(testParams.inputDuration),
        testParams.expectedDuration
      )
    })
  })
})

describe('formatDuration (with days)', () => {
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
      assert.equal(
        formatDuration(testParams.inputDuration, true),
        testParams.expectedDuration
      )
    })
  })
})
