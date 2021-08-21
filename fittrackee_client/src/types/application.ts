export interface IAppStatistics {
  sports: number
  uploads_dir_size: number
  users: number
  workouts: number
}

export interface IAppConfig {
  federation_enabled: boolean
  gpx_limit_import: number | null
  is_registration_enabled: boolean
  map_attribution: string
  max_single_file_size: number | null
  max_users: number | null
  max_zip_file_size: number | null
}

export interface IApplication {
  statistics: IAppStatistics
  config: IAppConfig
}
