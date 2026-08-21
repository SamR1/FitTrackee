export interface ITileProvider {
  attribution: string
  default: boolean
  name: string
  id: string
  enabled: boolean
}

export interface ITileProviderForAdmin extends ITileProvider {
  api_key_is_missing: boolean
}

export interface ITileProviderPayload {
  id: string
  default?: boolean
  enabled?: boolean
}
