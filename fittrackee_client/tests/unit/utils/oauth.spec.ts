import { describe, it, expect } from 'vitest'

import { isUriSchemeValid } from '@/utils/oauth'

describe('isUriSchemeValid', () => {
  const testsParams = [
    {
      inputRedirectUri: 'https://example.com/callback',
      expectedValue: true,
    },
    {
      inputRedirectUri: 'http://localhost:5000/callback',
      expectedValue: true,
    },
    {
      inputRedirectUri: 'example.com/callback',
      expectedValue: false,
    },
    {
      inputRedirectUri: 'invalid',
      expectedValue: false,
    },
    {
      inputRedirectUri: "javascript:alert('Hello, world!')",
      expectedValue: false,
    },
  ]

  testsParams.map((testParams) => {
    it(`returns ${testParams.inputRedirectUri} as ${testParams.expectedValue ? '' : 'in'}valid`, () => {
      expect(isUriSchemeValid(testParams.inputRedirectUri)).toStrictEqual(
        testParams.expectedValue
      )
    })
  })
})
