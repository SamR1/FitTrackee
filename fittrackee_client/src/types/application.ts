export interface IAppStatistics {
  sports: number
  uploads_dir_size: number
  users: number
  workouts: number
}

export type TAppConfig = {
  [key: string]: number | boolean | string | null
  about: string | null
  admin_contact: string
  federation_enabled: boolean
  gpx_limit_import: number
  is_email_sending_enabled: boolean
  is_registration_enabled: boolean
  map_attribution: string
  max_single_file_size: number
  max_users: number
  max_zip_file_size: number
  privacy_policy: string | null
  privacy_policy_date: string | null
  version: string
  weather_provider: string | null
}

export interface IDisplayOptions {
  dateFormat: string
  displayAscent: boolean
  timezone: string
  useImperialUnits: boolean
}
export interface IApplication {
  statistics: IAppStatistics
  config: TAppConfig
  displayOptions: IDisplayOptions
}

export type TAppConfigForm = {
  [key: string]: number | string | boolean
  about: string
  admin_contact: string
  federation_enabled: boolean
  gpx_limit_import: number
  max_single_file_size: number
  max_users: number
  max_zip_file_size: number
  privacy_policy: string
}
