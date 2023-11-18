import { describe, it, expect } from 'vitest'

import {
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
    assert.equal(linkifyAndClean('@foo@example.com'), '@foo@example.com')
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
      inputString: '<p class="active">test</p>',
      expectedString: '<p>test</p>',
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
      assert.equal(
        linkifyAndClean(testParams.inputString),
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
    console.log(linkifyAndClean(testParams.inputString))
    it(testParams.description, () => {
      expect(linkifyAndClean(testParams.inputString)).toBe(
        testParams.expectedString
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
      assert.deepEqual(
        getUsernameQuery(testParams.inputString),
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
      expectedString: 'Hello @Sam',
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
      assert.equal(
        replaceUsername(
          testParams.inputText,
          testParams.inputPosition,
          testParams.inputUsernameQuery,
          testParams.inputUsername
        ),
        testParams.expectedString
      )
    })
  })
})
