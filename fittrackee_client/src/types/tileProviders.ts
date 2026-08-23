export interface ITileProvider {
  attribution: string
  default: boolean
  default_for_user: boolean
  enabled: boolean
  name: string
  id: string
  link: string
}

export interface ITileProviderForAdmin extends ITileProvider {
  api_key_is_missing: boolean
  set_by_users: boolean
}

export interface ITileProviderPayload {
  id: string
  default?: boolean
  enabled?: boolean
}
