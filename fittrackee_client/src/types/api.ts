export interface IPagination {
  has_next: boolean
  has_prev: boolean
  page: number
  pages: number
  total: number
}

export type TPaginationPayload = {
  [key: string]: string | number
  order: string
  order_by: string
  per_page: number
  page: number
}
