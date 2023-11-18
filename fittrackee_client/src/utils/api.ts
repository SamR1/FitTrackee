import type { LocationQuery } from 'vue-router'

import type { IQueryOptions, TPaginationPayload } from '@/types/api'

export const sortList: string[] = ['asc', 'desc']
export const defaultPage = 1
export const defaultPerPage = 10

export const getNumberQueryValue = (
  queryValue: string | (string | null)[] | null,
  defaultValue: number
): number => {
  return queryValue && typeof queryValue === 'string' && +queryValue > 0
    ? +queryValue
    : defaultValue
}

export const getStringQueryValue = (
  queryValue: string | (string | null)[] | null,
  availableValues: string[],
  defaultValue: string
): string => {
  return queryValue &&
    typeof queryValue === 'string' &&
    availableValues.includes(queryValue)
    ? queryValue
    : defaultValue
}

export const getQuery = (
  locationQuery: LocationQuery,
  orderByList: string[],
  defaultOrderBy: string,
  options?: IQueryOptions
): TPaginationPayload => {
  const queryOptions = options || {}
  const defaultSort = queryOptions.defaultSort || 'asc'
  const query = <TPaginationPayload>{}

  query.page = getNumberQueryValue(locationQuery.page, defaultPage)
  query.per_page = getNumberQueryValue(locationQuery.per_page, defaultPerPage)
  query.order = getStringQueryValue(locationQuery.order, sortList, defaultSort)
  query.order_by = getStringQueryValue(
    locationQuery.order_by,
    orderByList,
    defaultOrderBy
  )
  if (typeof locationQuery.q === 'string') {
    query.q = locationQuery.q
  } else {
    delete query.q
  }
  if (typeof locationQuery.object_type === 'string') {
    query.object_type = locationQuery.object_type
  }
  if (typeof locationQuery.resolved === 'string') {
    query.resolved = locationQuery.resolved
  }

  return query
}

export const workoutsPayloadKeys = [
  'from',
  'to',
  'ave_speed_from',
  'ave_speed_to',
  'max_speed_from',
  'max_speed_to',
  'distance_from',
  'distance_to',
  'duration_from',
  'duration_to',
  'sport_id',
  'title',
]

const getRange = (stop: number, start = 1): number[] => {
  return Array.from({ length: stop - start + 1 }, (_, i) => start + i)
}

export const rangePagination = (
  pages: number,
  currentPage: number
): (string | number)[] => {
  if (pages < 0) {
    return []
  }

  if (pages < 9) {
    return getRange(pages)
  }

  let pagination: (string | number)[] = [1, 2]
  if (currentPage < 4) {
    pagination = pagination.concat([3, 4, 5])
  } else if (currentPage < 6) {
    pagination = pagination.concat(getRange(currentPage + 2, 3))
  } else {
    pagination = pagination.concat(['...'])
    if (currentPage < pages - 2) {
      pagination = pagination.concat(getRange(currentPage + 2, currentPage - 2))
    }
  }
  if (currentPage + 2 <= pages - 2) {
    pagination = pagination.concat(['...'])
    pagination = pagination.concat(getRange(pages, pages - 1))
  } else {
    if (
      pagination[pagination.length - 1] !== '...' &&
      +pagination[pagination.length - 1] >= pages - 2 &&
      +pagination[pagination.length - 1] < pages
    ) {
      pagination = pagination.concat(
        getRange(pages, +pagination[pagination.length - 1] + 1)
      )
    } else {
      pagination = pagination.concat(
        getRange(
          pages,
          currentPage < pages - 3 ? currentPage + 3 : currentPage - 5
        )
      )
    }
  }

  return pagination
}
