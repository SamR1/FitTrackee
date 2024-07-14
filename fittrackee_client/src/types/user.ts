import type { LocationQueryValue } from 'vue-router'

import type { IPagePayload, TPaginationPayload } from '@/types/api'
import type { TLanguage } from '@/types/locales'
import type { IRecord } from '@/types/workouts'

export type TPrivacyLevels = 'private' | 'followers_only' | 'public'
export type TRelationshipAction = 'follow' | 'unfollow' | 'block' | 'unblock'
export type TRelationships = 'followers' | 'following'
export type TFollowRequestAction = 'accept' | 'reject'

export interface IUserLightProfile {
  admin: boolean
  created_at: string
  picture: string | boolean
  username: string
}

export interface IUserProfile extends IUserLightProfile {
  bio: string | null
  birth_date: string | null
  blocked: boolean
  email?: string
  email_to_confirm?: string
  is_active: boolean
  first_name: string | null
  followers: IUserProfile[]
  following: IUserProfile[]
  follows: string
  is_followed_by: string
  last_name: string | null
  location: string | null
  nb_sports?: number
  nb_workouts: number
  profile_link?: string
  records: IRecord[]
  sports_list: number[]
  suspended_at: string | null
  total_ascent: number
  total_distance: number
  total_duration: string
}

export interface IAuthUserProfile extends IUserProfile {
  accepted_privacy_policy: boolean
  display_ascent: boolean
  email: string
  hide_profile_in_users_directory: boolean
  imperial_units: boolean
  start_elevation_at_zero: boolean
  use_raw_gpx_speed: boolean
  language: TLanguage | null
  manually_approves_followers: boolean
  map_visibility: TPrivacyLevels
  nb_sports: number
  records: IRecord[]
  sports_list: number[]
  timezone: string
  date_format: string
  total_distance: number
  total_duration: string
  weekm: boolean
  use_dark_mode: boolean | null
  workouts_visibility: TPrivacyLevels
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
  activate?: boolean
  admin?: boolean
  new_email?: string
  resetPassword?: boolean
  username: string
}

export interface IUserRelationshipActionPayload {
  username: string
  action: TRelationshipAction
  from: string
  payload?: IPagePayload
}

export interface IUserPreferencesPayload {
  date_format: string
  display_ascent: boolean
  hide_profile_in_users_directory: boolean
  imperial_units: boolean
  language: TLanguage
  manually_approves_followers: boolean
  map_visibility: TPrivacyLevels
  start_elevation_at_zero: boolean
  timezone: string
  use_raw_gpx_speed: boolean
  weekm: boolean
  use_dark_mode: boolean | null
  workouts_visibility: TPrivacyLevels
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

export type TUsersPayload = TPaginationPayload & {
  username?: string
}

export interface IUserRelationshipsPayload {
  username: string
  relationship: TRelationships
  page: number
}

export interface IFollowRequestsActionPayload {
  username: string
  action: TFollowRequestAction
  getFollowRequests?: boolean
}

export interface ISuspensionAppeal {
  approved: boolean | null
  created_at: string
  id: string
  reason: string | null
  text: string
  updated_at: string
}

export interface ISuspension {
  action_type: string
  appeal: ISuspensionAppeal
  created_at: string
  id: string
  reason: string
  user?: IUserProfile
}
