import { assert } from 'chai'

import { TPrivacyLevels } from '@/types/user'
import {
  getCommentVisibilityLevels,
  getMapVisibilityLevels,
  getUpdatedMapVisibility,
} from '@/utils/privacy'

describe('getUpdatedMapVisibility', () => {
  const testsParams: [TPrivacyLevels, TPrivacyLevels, TPrivacyLevels][] = [
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
      assert.equal(
        getUpdatedMapVisibility(testParams[0], testParams[1]),
        testParams[2]
      )
    })
  })
})

describe('getMapVisibilityLevels', () => {
  const testsParams: [TPrivacyLevels, TPrivacyLevels[]][] = [
    ['private', ['private']],
    ['followers_only', ['private', 'followers_only']],
    ['public', ['private', 'followers_only', 'public']],
  ]

  testsParams.map((testParams) => {
    it(`get visibility levels depending on workout visibility (input value: '${testParams[0]}')`, () => {
      assert.deepEqual(getMapVisibilityLevels(testParams[0]), testParams[1])
    })
  })
})

describe('getCommentVisibilityLevels', () => {
  const testsParams: [TPrivacyLevels, TPrivacyLevels[]][] = [
    ['private', ['private']],
    ['followers_only', ['private', 'followers_only']],
    ['public', ['private', 'followers_only', 'public']],
  ]

  testsParams.map((testParams) => {
    it(`get visibility levels depending on workout visibility',input value: '${testParams[1]}')`, () => {
      assert.deepEqual(getCommentVisibilityLevels(testParams[0]), testParams[1])
    })
  })
})
