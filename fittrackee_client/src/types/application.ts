export interface IAppStatistics {
  sports: number
  uploads_dir_size: number
  users: number
  workouts: number
}

export type TAppConfig = {
  [key: string]: number | boolean | string
  federation_enabled: boolean
  gpx_limit_import: number
  is_registration_enabled: boolean
  map_attribution: string
  max_single_file_size: number
  max_users: number
  max_zip_file_size: number
}

export interface IApplication {
  statistics: IAppStatistics
  config: TAppConfig
}

export type TAppConfigForm = {
  [key: string]: number
  gpx_limit_import: number
  max_single_file_size: number
  max_users: number
  max_zip_file_size: number
}
