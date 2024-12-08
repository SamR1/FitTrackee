import { describe, it, expect } from 'vitest'

import { TVisibilityLevels } from '@/types/user'
import {
  getCommentVisibilityLevels,
  getMapVisibilityLevels,
  getUpdatedMapVisibility,
} from '@/utils/visibility_levels'

describe('getUpdatedMapVisibility', () => {
  const testsParams: [
    TVisibilityLevels,
    TVisibilityLevels,
    TVisibilityLevels,
  ][] = [
    // input map visibility, input workout visibility, excepted map visibility
    ['private', 'private', 'private'],
    ['private', 'followers_only', 'private'],
    ['private', 'public', 'private'],
    ['followers_only', 'private', 'private'],
    ['followers_only', 'followers_only', 'followers_only'],
    ['followers_only', 'public', 'followers_only'],
    ['public', 'private', 'private'],
    ['public', 'followers_only', 'followers_only'],
    ['public', 'public', 'public'],
  ]

  testsParams.map((testParams) => {
    it(`get map visibility (input value: '${testParams[0]}') when workout visibility is '${testParams[1]}'`, () => {
      expect(
        getUpdatedMapVisibility(testParams[0], testParams[1])
      ).toStrictEqual(testParams[2])
    })
  })
})

describe('getMapVisibilityLevels', () => {
  const testsParams: [TVisibilityLevels, TVisibilityLevels[]][] = [
    ['private', ['private']],
    ['followers_only', ['private', 'followers_only']],
    ['public', ['private', 'followers_only', 'public']],
  ]

  testsParams.map((testParams) => {
    it(`get visibility levels depending on workout visibility (input value: '${testParams[0]}')`, () => {
      expect(getMapVisibilityLevels(testParams[0])).toStrictEqual(testParams[1])
    })
  })
})

describe('getCommentVisibilityLevels', () => {
  const testsParams: [TVisibilityLevels, TVisibilityLevels[]][] = [
    ['private', ['private']],
    ['followers_only', ['private', 'followers_only']],
    ['public', ['private', 'followers_only', 'public']],
  ]

  testsParams.map((testParams) => {
    it(`get visibility levels depending on workout visibility',input value: '${testParams[1]}')`, () => {
      expect(getCommentVisibilityLevels(testParams[0])).toStrictEqual(
        testParams[1]
      )
    })
  })
})
