import { assert } from 'chai'

import { getReadableFileSize } from '@/utils/files'

describe('getReadableFileSize (as text)', () => {
  const testsParams = [
    {
      description: 'returns 0 bytes if provided file size is 0',
      inputFileSize: 0,
      expectedReadableFileSize: '0 bytes',
    },
    {
      description: 'returns 1.0KB if provided file size is 1024',
      inputFileSize: 1024,
      expectedReadableFileSize: '1.0KB',
    },
    {
      description: 'returns 43.5MB if provided file size is 45654654',
      inputFileSize: 45654654,
      expectedReadableFileSize: '43.5MB',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.equal(
        getReadableFileSize(testParams.inputFileSize, true),
        testParams.expectedReadableFileSize
      )
    })
  })
})

describe('getReadableFileSize (as object)', () => {
  const testsParams = [
    {
      description: 'returns 0 bytes if provided file size is 0',
      inputFileSize: 0,
      expectedReadableFileSize: { size: '0', suffix: 'bytes' },
    },
    {
      description: 'returns 1.0KB if provided file size is 1024',
      inputFileSize: 1024,
      expectedReadableFileSize: { size: '1.0', suffix: 'KB' },
    },
    {
      description: 'returns 43.5MB if provided file size is 45654654',
      inputFileSize: 45654654,
      expectedReadableFileSize: { size: '43.5', suffix: 'MB' },
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.deepEqual(
        getReadableFileSize(testParams.inputFileSize, false),
        testParams.expectedReadableFileSize
      )
    })
  })
})
