import { describe, it, expect } from 'vitest'

import { linkifyAndClean } from '@/utils/inputs'

describe('linkifyAndClean (clean input remains unchanged)', () => {
  const testInputs = [
    'just a text\nfor "test"',
    'link: <a href="http://www.example.com">example</a>',
    'link: <a href="http://www.example.com" target="_blank">example</a>',
  ]

  testInputs.map((testInput) => {
    it(`it returns unmodified input: '${testInput}'`, () => {
      expect(linkifyAndClean(testInput)).toBe(testInput)
    })
  })
})

describe('linkifyAndClean (URL is linkified)', () => {
  it('it returns URL as link with target blank', () => {
    expect(linkifyAndClean('link: http://www.example.com')).toBe(
      'link: <a href="http://www.example.com" target="_blank">http://www.example.com</a>'
    )
  })
})

describe('linkifyAndClean (input sanitization)', () => {
  const testsParams = [
    {
      description: 'it escapes "script" tags',
      inputString: "<script>alert('evil!')</script>",
      expectedString: "&lt;script&gt;alert('evil!')&lt;/script&gt;",
    },
    {
      description: 'it escapes nested tags',
      inputString: '<p><b>test</b></p>',
      expectedString: '&lt;p&gt;&lt;b&gt;test&lt;/b&gt;&lt;/p&gt;',
    },
    {
      description: 'it escapes single tag',
      inputString: '<p>test',
      expectedString: '&lt;p&gt;test',
    },
    {
      description: 'it removes css classe',
      inputString: '<div class="active">test</div>',
      expectedString: '&lt;div&gt;test&lt;/div&gt;',
    },
    {
      description: 'it removes style attribute',
      inputString: '<div style="display:none;">test</div>',
      expectedString: '&lt;div&gt;test&lt;/div&gt;',
    },
    {
      description: 'it keeps nested HTML link',
      inputString: '<p><a href="http://www.example.com">example</a></p>',
      expectedString:
        '&lt;p&gt;<a href="http://www.example.com">example</a>&lt;/p&gt;',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(linkifyAndClean(testParams.inputString)).toBe(
        testParams.expectedString
      )
    })
  })
})
