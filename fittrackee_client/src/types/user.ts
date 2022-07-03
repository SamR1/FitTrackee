import { LocationQueryValue } from 'vue-router'

import { IRecord } from '@/types/workouts'

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
  total_distance: number
  total_duration: string
  username: string
}

export interface IAuthUserProfile extends IUserProfile {
  imperial_units: boolean
  language: string | null
  timezone: string
  weekm: boolean
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
  imperial_units: boolean
  language: string
  timezone: string
  weekm: boolean
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
  language?: string
}

export interface ILoginOrRegisterData {
  actionType: string
  formData: ILoginRegisterFormData
  redirectUrl?: string | null | LocationQueryValue[]
}
