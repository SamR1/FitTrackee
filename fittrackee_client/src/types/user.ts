import { LocationQueryValue } from 'vue-router'

import { IRecord } from '@/types/workouts'

export type TPrivacyLevels = 'private' | 'followers_only' | 'public'

export interface IUserProfile {
  admin: boolean
  bio: string | null
  birth_date: string | null
  created_at: string
  email?: string
  first_name: string | null
  followers: IUserProfile[]
  following: IUserProfile[]
  last_name: string | null
  location: string | null
  map_visibility: TPrivacyLevels
  nb_sports?: number
  nb_workouts: number
  picture: string | boolean
  records?: IRecord[]
  sports_list?: number[]
  total_distance?: number
  total_duration?: string
  username: string
  workouts_visibility: TPrivacyLevels
}

export interface IAuthUserProfile extends IUserProfile {
  email: string
  imperial_units: boolean
  language: string | null
  nb_sports: number
  records: IRecord[]
  sports_list: number[]
  timezone: string
  total_distance: number
  total_duration: string
  weekm: boolean
}

export interface IUserPayload {
  bio: string
  birth_date: string
  first_name: string
  last_name: string
  location: string
  password: string
  password_conf: string
}

export interface IAdminUserPayload {
  username: string
  admin: boolean
}

export interface IUserPreferencesPayload {
  imperial_units: boolean
  language: string
  map_visibility: TPrivacyLevels
  timezone: string
  weekm: boolean
  workouts_visibility: TPrivacyLevels
}

export interface IUserSportPreferencesPayload {
  sport_id: number
  color: string | null
  is_active: boolean
  stopped_speed_threshold: number
}

export interface IUserPicturePayload {
  picture: File
}

export interface IUserPasswordPayload {
  email: string
}

export interface IUserPasswordResetPayload {
  password: string
  password_conf: string
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
  password_conf: string
}

export interface ILoginOrRegisterData {
  actionType: string
  formData: ILoginRegisterFormData
  redirectUrl?: string | null | LocationQueryValue[]
}
