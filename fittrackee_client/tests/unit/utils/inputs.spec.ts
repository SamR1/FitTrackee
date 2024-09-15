import { describe, it, expect } from 'vitest'

import { convertToMarkdown, linkifyAndClean } from '@/utils/inputs'

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
      description: 'it removes css class',
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

describe('convertToMarkdown', () => {
  const testInputs: Record<string, string>[] = [
    {
      inputString: 'just a **text**',
      expectedString: '<p>just a <strong>text</strong></p>\n',
    },
    {
      inputString: '_italic_',
      expectedString: '<p><em>italic</em></p>\n',
    },
    {
      inputString: 'http://www.example.com',
      expectedString:
        '<p><a href="http://www.example.com">http://www.example.com</a></p>\n',
    },
    {
      inputString: '[example](http://www.example.com)',
      expectedString: '<p><a href="http://www.example.com">example</a></p>\n',
    },
    {
      inputString:
        '<a href="http://www.example.com">http://www.example.com</a>',
      expectedString:
        '<p><a href="http://www.example.com">http://www.example.com</a></p>\n',
    },
  ]

  testInputs.map((testInput) => {
    it(`it returns input as html: '${testInput.inputString}'`, () => {
      expect(convertToMarkdown(testInput.inputString)).toBe(
        testInput.expectedString
      )
    })
  })
})

describe('convertToMarkdown (sanitization)', () => {
  const testInputs: Record<string, string>[] = [
    {
      description: 'it removes script',
      inputString: "test <script>alert('evil!')</script>",
      expectedString: '<p>test </p>\n',
    },
    {
      description: 'it removes css class',
      inputString: '<div class="active">test</div>',
      expectedString: '<div>test</div>',
    },
    {
      description: 'it removes style attribute',
      inputString: '<div style="display:none;">test</div>',
      expectedString: '<div>test</div>',
    },
    {
      description: 'it closes single tags',
      inputString: '<p><strong>test',
      expectedString: '<p><strong>test</strong></p>',
    },
  ]

  testInputs.map((testInput) => {
    it(`${testInput.description}: '${testInput.inputString}'`, () => {
      expect(convertToMarkdown(testInput.inputString)).toBe(
        testInput.expectedString
      )
    })
  })
})
