import { describe, it, expect } from 'vitest'

import {
  defaultPerPage,
  defaultPage,
  sortList,
  getNumberQueryValue,
  getStringQueryValue,
  getQuery,
  rangePagination,
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
      expect(
        getNumberQueryValue(testParams.inputValue, testParams.inputDefaultValue)
      ).toBe(testParams.expectedValue)
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
      expect(
        getStringQueryValue(
          testParams.inputValue,
          sortList,
          testParams.inputDefaultValue
        )
      ).toBe(testParams.expectedValue)
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
      expect(
        getQuery(testParams.inputLocationQuery, orderByList, defaultOrderBy, {
          defaultSort,
        })
      ).toStrictEqual(testParams.expectedQuery)
    })
  })
})

describe('getQuery w/ default values', () => {
  it('returns default query if location query is an empty object', () => {
    expect(getQuery({}, orderByList, defaultOrderBy)).toStrictEqual({
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
    expect(
      getQuery({}, orderByList, defaultOrderBy, { query: inputQuery })
    ).toStrictEqual({
      page: 1,
      per_page: 10,
      order: 'asc',
      order_by: defaultOrderBy,
    })
  })

  it('returns query updated with input values', () => {
    expect(
      getQuery({}, orderByList, defaultOrderBy, {
        defaultSort: 'desc',
        query: inputQuery,
      })
    ).toStrictEqual({
      page: 1,
      per_page: 10,
      order: 'desc',
      order_by: defaultOrderBy,
    })
  })

  it('returns query updated', () => {
    expect(
      getQuery(
        { page: '3', per_page: '10', order: 'asc', order_by: 'workouts_count' },
        orderByList,
        defaultOrderBy,
        { query: inputQuery }
      )
    ).toStrictEqual({
      page: 3,
      per_page: 10,
      order: 'asc',
      order_by: 'workouts_count',
    })
  })

  it('returns query with only pagination keys', () => {
    expect(
      getQuery(
        {
          page: '3',
          per_page: '10',
          order: 'asc',
          order_by: 'workouts_count',
          sport_id: '1',
        },
        orderByList,
        defaultOrderBy,
        { query: inputQuery }
      )
    ).toStrictEqual({
      page: 3,
      per_page: 10,
      order: 'asc',
      order_by: 'workouts_count',
    })
  })
})

describe('rangePagination', () => {
  const testsParams = [
    {
      description: 'returns empty array if pages total equals 0',
      input: {
        currentPage: 1,
        pages: 0,
      },
      expectedPagination: [],
    },
    {
      description: 'returns empty array if pages total is a negative value',
      input: {
        currentPage: 1,
        pages: -1,
      },
      expectedPagination: [],
    },
    {
      description:
        'returns pagination if current page is 1 and pages total equals 1',
      input: {
        currentPage: 1,
        pages: 1,
      },
      expectedPagination: [1],
    },
    {
      description:
        'returns pagination if current page is 1 and pages total equals 4',
      input: {
        currentPage: 1,
        pages: 4,
      },
      expectedPagination: [1, 2, 3, 4],
    },
    {
      description:
        'returns pagination if current page is 4 and pages total equals 8',
      input: {
        currentPage: 4,
        pages: 8,
      },
      expectedPagination: [1, 2, 3, 4, 5, 6, 7, 8],
    },
    {
      description: 'returns pagination if current page is 1 and total pages 10',
      input: {
        currentPage: 1,
        pages: 10,
      },
      expectedPagination: [1, 2, 3, 4, 5, '...', 9, 10],
    },
    {
      description:
        'returns pagination if current page is 4 and pages total equals 10',
      input: {
        currentPage: 4,
        pages: 10,
      },
      expectedPagination: [1, 2, 3, 4, 5, 6, '...', 9, 10],
    },
    {
      description:
        'returns pagination if current page is 7 and pages total equals 10',
      input: {
        currentPage: 7,
        pages: 10,
      },
      expectedPagination: [1, 2, '...', 5, 6, 7, 8, 9, 10],
    },
    {
      description:
        'returns pagination if current page is 20 and pages total equals 30',
      input: {
        currentPage: 20,
        pages: 30,
      },
      expectedPagination: [1, 2, '...', 18, 19, 20, 21, 22, '...', 29, 30],
    },
    {
      description:
        'returns pagination if current page is 1 and total pages 100',
      input: {
        currentPage: 1,
        pages: 100,
      },
      expectedPagination: [1, 2, 3, 4, 5, '...', 99, 100],
    },
    {
      description:
        'returns pagination if current page is 5 and total pages 100',
      input: {
        currentPage: 5,
        pages: 100,
      },
      expectedPagination: [1, 2, 3, 4, 5, 6, 7, '...', 99, 100],
    },
    {
      description:
        'returns pagination if current page is 50 and total pages 100',
      input: {
        currentPage: 50,
        pages: 100,
      },
      expectedPagination: [1, 2, '...', 48, 49, 50, 51, 52, '...', 99, 100],
    },
    {
      description:
        'returns pagination if current page is 97 and total pages 100',
      input: {
        currentPage: 97,
        pages: 100,
      },
      expectedPagination: [1, 2, '...', 95, 96, 97, 98, 99, 100],
    },
    {
      description:
        'returns pagination if current page is 100 and total pages 100',
      input: {
        currentPage: 100,
        pages: 100,
      },
      expectedPagination: [1, 2, '...', 95, 96, 97, 98, 99, 100],
    },
  ]

  testsParams.map((testParams) => {
    it(testParams.description, () => {
      expect(
        rangePagination(testParams.input.pages, testParams.input.currentPage)
      ).toStrictEqual(testParams.expectedPagination)
    })
  })
})
