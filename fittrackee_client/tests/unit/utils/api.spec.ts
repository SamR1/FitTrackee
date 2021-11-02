import { assert } from 'chai'

import {
  defaultPerPage,
  defaultPage,
  sortList,
  getNumberQueryValue,
  getStringQueryValue,
  getQuery,
} from '@/utils/api'

const orderByList = ['admin', 'created_at', 'username', 'workouts_count']
const defaultSort = 'desc'
const defaultOrderBy = 'created_at'

const generateLocationQuery = (
  query: Record<string, string>
): Record<string, string | (string | null)[] | null> => {
  return query
}

describe('getNumberQueryValue', () => {
  const testsParams = [
    {
      description: 'returns 2 if input value is 2',
      inputValue: '2',
      inputDefaultValue: 2,
      expectedValue: 2,
    },
    {
      description: 'returns default value if input value is null',
      inputValue: null,
      inputDefaultValue: 1,
      expectedValue: 1,
    },
    {
      description: 'returns default value if input value is negative value',
      inputValue: '-1',
      inputDefaultValue: 1,
      expectedValue: 1,
    },
    {
      description: 'returns default value if input value is not a number',
      inputValue: 'a',
      inputDefaultValue: 1,
      expectedValue: 1,
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.equal(
        getNumberQueryValue(
          testParams.inputValue,
          testParams.inputDefaultValue
        ),
        testParams.expectedValue
      )
    })
  })
})

describe('getStringQueryValue', () => {
  const testsParams = [
    {
      description: 'returns input value if input value is in list',
      inputValue: 'asc',
      inputDefaultValue: 'asc',
      expectedValue: 'asc',
    },
    {
      description: 'returns default value if input value is null',
      inputValue: null,
      inputDefaultValue: 'asc',
      expectedValue: 'asc',
    },
    {
      description: 'returns default value if input value is not in list',
      inputValue: '1',
      inputDefaultValue: 'asc',
      expectedValue: 'asc',
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.equal(
        getStringQueryValue(
          testParams.inputValue,
          sortList,
          testParams.inputDefaultValue
        ),
        testParams.expectedValue
      )
    })
  })
})

describe('getQuery', () => {
  const testsParams = [
    {
      description: 'returns default query if location query is an empty object',
      inputLocationQuery: {},
      expectedQuery: {
        page: defaultPage,
        per_page: defaultPerPage,
        order: defaultSort,
        order_by: defaultOrderBy,
      },
    },
    {
      description: 'returns query with input page',
      inputLocationQuery: generateLocationQuery({ page: '2' }),
      expectedQuery: {
        page: 2,
        per_page: defaultPerPage,
        order: defaultSort,
        order_by: defaultOrderBy,
      },
    },
    {
      description: 'returns query with input per_page',
      inputLocationQuery: generateLocationQuery({ per_page: '20' }),
      expectedQuery: {
        page: defaultPage,
        per_page: 20,
        order: defaultSort,
        order_by: defaultOrderBy,
      },
    },
    {
      description: 'returns query with input order',
      inputLocationQuery: generateLocationQuery({ order: 'asc' }),
      expectedQuery: {
        page: defaultPage,
        per_page: defaultPerPage,
        order: 'asc',
        order_by: defaultOrderBy,
      },
    },
    {
      description: 'returns query with input order_by',
      inputLocationQuery: generateLocationQuery({ order_by: 'username' }),
      expectedQuery: {
        page: defaultPage,
        per_page: defaultPerPage,
        order: defaultSort,
        order_by: 'username',
      },
    },
    {
      description:
        'returns default query with input location query values are invalid',
      inputLocationQuery: generateLocationQuery({
        page: '0',
        per_page: '0',
        order: 'random',
        order_by: 'name',
      }),
      expectedQuery: {
        page: defaultPage,
        per_page: defaultPerPage,
        order: defaultSort,
        order_by: defaultOrderBy,
      },
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.deepEqual(
        getQuery(testParams.inputLocationQuery, orderByList, defaultOrderBy, {
          defaultSort,
        }),
        testParams.expectedQuery
      )
    })
  })
})

describe('getQuery w/ default values', () => {
  it('returns default query if location query is an empty object', () => {
    assert.deepEqual(getQuery({}, orderByList, defaultOrderBy), {
      page: 1,
      per_page: 10,
      order: 'asc',
      order_by: defaultOrderBy,
    })
  })
})

describe('getQuery w/ default values and input pagination payload', () => {
  const inputQuery = {
    page: 2,
    per_page: 20,
    order: 'desc',
    order_by: 'username',
  }

  it('returns query updated with default values', () => {
    assert.deepEqual(
      getQuery({}, orderByList, defaultOrderBy, { query: inputQuery }),
      {
        page: 1,
        per_page: 10,
        order: 'asc',
        order_by: defaultOrderBy,
      }
    )
  })

  it('returns query updated with input values', () => {
    assert.deepEqual(
      getQuery({}, orderByList, defaultOrderBy, {
        defaultSort: 'desc',
        query: inputQuery,
      }),
      {
        page: 1,
        per_page: 10,
        order: 'desc',
        order_by: defaultOrderBy,
      }
    )
  })

  it('returns query updated', () => {
    assert.deepEqual(
      getQuery(
        { page: '3', per_page: '10', order: 'asc', order_by: 'workouts_count' },
        orderByList,
        defaultOrderBy,
        { query: inputQuery }
      ),
      { page: 3, per_page: 10, order: 'asc', order_by: 'workouts_count' }
    )
  })
})
