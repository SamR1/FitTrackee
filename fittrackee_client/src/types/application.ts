import type { IUserLightProfile } from '@/types/user.ts'

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
  gpx_limit_import: number
  is_email_sending_enabled: boolean
  is_registration_enabled: boolean
  map_attribution: string
  max_single_file_size: number
  max_users: number
  max_zip_file_size: number
  privacy_policy: string | null
  privacy_policy_date: string
  stats_workouts_limit: number
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
  file_limit_import: number
  file_sync_limit_import: number
  max_single_file_size: number
  max_users: number
  max_zip_file_size: number
  privacy_policy: string
}

export interface IFileSize {
  size: string
  suffix: string
}

export type TTaskType = 'user_data_export' | 'workouts_archive_upload'

export type TQueuedTasksCounts = {
  [key in TTaskType]: number
}

export interface IQueuedTask {
  file_size: number
  created_at: string
  id: string
  message_id: string
  files_count?: number
  user: IUserLightProfile
}

export interface IQueuedTasksPayload {
  page?: number
  taskType: string
}
