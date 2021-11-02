import { LocationQuery } from 'vue-router'

import { IQueryOptions, TPaginationPayload } from '@/types/api'

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
  const query = queryOptions.query || <TPaginationPayload>{}

  query.page = getNumberQueryValue(locationQuery.page, defaultPage)
  query.per_page = getNumberQueryValue(locationQuery.per_page, defaultPerPage)
  query.order = getStringQueryValue(locationQuery.order, sortList, defaultSort)
  query.order_by = getStringQueryValue(
    locationQuery.order_by,
    orderByList,
    defaultOrderBy
  )

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
]
