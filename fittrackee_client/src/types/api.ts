export interface IPagination {
  has_next: boolean
  has_prev: boolean
  page: number
  pages: number
  total: number
}

export type TPaginationPayload = {
  [key: string]: string | number | undefined
  order?: string
  order_by?: string
  per_page?: number
  page?: number
  q?: string
}

export interface IQueryOptions {
  defaultSort?: string
  query?: TPaginationPayload
}

export interface IApiErrorMessage {
  error?: string
  message?: string
}

export interface IPagePayload {
  page: number
}
