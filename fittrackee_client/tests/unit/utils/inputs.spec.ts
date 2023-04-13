import { assert } from 'chai'

import { linkifyAndClean } from '@/utils/inputs'

describe('linkifyAndClean (clean input remains unchanged)', () => {
  const testInputs = [
    'just a text\nfor "test"',
    'link: <a href="http://www.example.com">example</a>',
    'link: <a href="http://www.example.com" target="_blank">example</a>',
  ]

  testInputs.map((testInput) => {
    it(`it returns unmodified input: '${testInput}'`, () => {
      assert.equal(linkifyAndClean(testInput), testInput)
    })
  })
})

describe('linkifyAndClean (URL is linkified)', () => {
  it('it returns URL as link with target blank', () => {
    assert.equal(
      linkifyAndClean('link: http://www.example.com'),
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
