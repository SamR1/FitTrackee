import type { LocationQueryValue } from 'vue-router'

import type { TLanguage } from '@/types/locales'
import type { IRecord } from '@/types/workouts'

export interface IUserProfile {
  admin: boolean
  bio: string | null
  birth_date: string | null
  created_at: string
  email: string
  email_to_confirm?: string
  is_active: boolean
  first_name: string | null
  last_name: string | null
  location: string | null
  nb_sports: number
  nb_workouts: number
  picture: string | boolean
  records: IRecord[]
  sports_list: number[]
  total_ascent: number
  total_distance: number
  total_duration: string
  username: string
}

export interface IAuthUserProfile extends IUserProfile {
  accepted_privacy_policy: boolean
  display_ascent: boolean
  imperial_units: boolean
  start_elevation_at_zero: boolean
  use_raw_gpx_speed: boolean
  language: TLanguage | null
  timezone: string
  date_format: string
  weekm: boolean
  use_dark_mode: boolean | null
}

export interface IUserPayload {
  bio: string
  birth_date: string
  first_name: string
  last_name: string
  location: string
}

export interface IUserAccountPayload {
  email: string
  password: string
  new_password?: string
}

export interface IUserAccountUpdatePayload {
  token: LocationQueryValue | LocationQueryValue[]
  refreshUser?: boolean
}

export interface IAdminUserPayload {
  username: string
  admin?: boolean
  resetPassword?: boolean
  activate?: boolean
  new_email?: string
}

export interface IUserPreferencesPayload {
  display_ascent: boolean
  start_elevation_at_zero: boolean
  use_raw_gpx_speed: boolean
  imperial_units: boolean
  language: TLanguage
  timezone: string
  date_format: string
  weekm: boolean
  use_dark_mode: boolean | null
}

export interface IUserSportPreferencesResetPayload {
  sportId: number
  fromSport: boolean
}

export interface IUserSportPreferencesPayload {
  sport_id: number
  color: string | null
  is_active: boolean
  stopped_speed_threshold: number
  fromSport: boolean
  default_equipment_ids?: string[]
}

export interface IUserPicturePayload {
  picture: File
}

export interface IUserEmailPayload {
  email: string
}

export interface IUserPasswordResetPayload {
  password: string
  token: string
}

export interface IUserDeletionPayload {
  username: string
  fromAdmin?: boolean
}

export interface ILoginRegisterFormData {
  username: string
  email: string
  password: string
  language?: TLanguage
  accepted_policy?: boolean
}

export interface ILoginOrRegisterData {
  actionType: string
  formData: ILoginRegisterFormData
  redirectUrl?: string | null | LocationQueryValue[]
}

export interface IExportRequest {
  created_at: string
  status: string
  file_name: string
  file_size: number
}
