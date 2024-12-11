import { describe, it, expect } from 'vitest'

import {
  convertToMarkdown,
  getUsernameQuery,
  linkifyAndClean,
  replaceUsername,
} from '@/utils/inputs'

describe('linkifyAndClean (clean input remains unchanged)', () => {
  const testInputs = [
    'just a text\nfor "test"',
    'link: <a href="http://www.example.com">example</a>',
    'link: <a href="http://www.example.com" target="_blank">example</a>',
    'just a <em>test</em>',
    'just a <strong>test</strong>',
    '<img src="http://www.example.com/pictures.png" alt="Image" title="icon" />',
    ':)',
    '😀',
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

  it('it does not return user fullname as mailto link', () => {
    expect(linkifyAndClean('@foo@example.com')).toBe('@foo@example.com')
  })
})

describe('linkifyAndClean (input sanitization)', () => {
  const testsParams = [
    {
      description: 'it removes "script" tags',
      inputString: "<script>alert('evil!')</script>",
      expectedString: '',
    },
    {
      description: 'it removes nested tags',
      inputString: '<div><b>test</b></div>',
      expectedString: 'test',
    },
    {
      description: 'it removes single tag',
      inputString: '<div>test',
      expectedString: 'test',
    },
    {
      description: 'it removes css class',
      inputString: '<div class="active">test</div>',
      expectedString: 'test',
    },
    {
      description: 'it removes style attribute',
      inputString: '<p style="display:none;">test</p>',
      expectedString: '<p>test</p>',
    },
    {
      description: 'it keeps nested HTML link',
      inputString: '<div><a href="http://www.example.com">example</a></div>',
      expectedString: '<a href="http://www.example.com">example</a>',
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

describe('linkifyAndClean with markdown', () => {
  const testsParams = [
    {
      description: 'it returns text with <strong> attribute',
      inputString: 'just a **test**',
      expectedString: 'just a <strong>test</strong>',
    },
    {
      description: 'it returns text with <em> attribute',
      inputString: 'just a _test_',
      expectedString: 'just a <em>test</em>',
    },
    {
      description: 'it returns link',
      inputString: 'just a [link](http://www.example.com)',
      expectedString: 'just a <a href="http://www.example.com">link</a>',
    },
    {
      description: 'it returns image',
      inputString: '![Image](http://www.example.com/pictures.png "icon")',
      expectedString:
        '<img src="http://www.example.com/pictures.png" alt="Image" title="icon" />',
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

describe('getUsernameQuery', () => {
  const testsParams = [
    {
      description: 'it returns null when no string starting with @',
      inputString: {
        value: 'hello User',
        selectionStart: 0,
      },
      expectedValues: {
        position: null,
        usernameQuery: null,
      },
    },
    {
      description:
        'it returns null when string staring with @ length is too short',
      inputString: {
        value: 'hello @U',
        selectionStart: 7,
      },
      expectedValues: {
        position: null,
        usernameQuery: null,
      },
    },
    {
      description:
        'it returns username query when string starts with @ (and cursor position at the end)',
      inputString: {
        value: 'hello @Us',
        selectionStart: 8,
      },
      expectedValues: {
        position: 6,
        usernameQuery: 'Us',
      },
    },
    {
      description:
        'it returns null when cursor position is not at the end of a string starting with @',
      inputString: {
        value: 'hello @User !',
        selectionStart: 12,
      },
      expectedValues: {
        position: null,
        usernameQuery: null,
      },
    },
    {
      description:
        'it returns username query when cursor position is at the end of a string starting with @',
      inputString: {
        value: 'hello @User !',
        selectionStart: 10,
      },
      expectedValues: {
        position: 6,
        usernameQuery: 'User',
      },
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(getUsernameQuery(testParams.inputString)).toStrictEqual(
        testParams.expectedValues
      )
    })
  })
})

describe('replaceUsername', () => {
  const testsParams = [
    {
      description:
        'it replaces username query with username when query is at the end',
      inputText: 'Hello @Sa',
      inputPosition: 6,
      inputUsernameQuery: 'Sa',
      inputUsername: 'Sam',
      expectedString: 'Hello @Sam ',
    },
    {
      description:
        'it replaces username query with username when query is not at the end',
      inputText: 'Hello @Sa !',
      inputPosition: 6,
      inputUsernameQuery: 'Sa',
      inputUsername: 'Sam',
      expectedString: 'Hello @Sam !',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        replaceUsername(
          testParams.inputText,
          testParams.inputPosition,
          testParams.inputUsernameQuery,
          testParams.inputUsername
        )
      ).toBe(testParams.expectedString)
    })
  })
})
