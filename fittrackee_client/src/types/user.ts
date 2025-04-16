import type { LocationQueryValue } from 'vue-router'

import type { IPagePayload, TPaginationPayload } from '@/types/api'
import type { TLanguage } from '@/types/locales'
import type { TNotificationPreferences } from '@/types/notifications.ts'
import type { IComment, IRecord, IWorkout } from '@/types/workouts'

export type TRelationshipAction = 'follow' | 'unfollow' | 'block' | 'unblock'
export type TRelationships = 'followers' | 'following'
export type TFollowRequestAction = 'accept' | 'reject'
export type TUserRole = 'user' | 'moderator' | 'admin' | 'owner'
export type TVisibilityLevels = 'private' | 'followers_only' | 'public'

export interface IUserLightProfile {
  blocked: boolean
  created_at: string
  followers: IUserProfile[]
  following: IUserProfile[]
  follows: string
  is_active?: boolean
  is_followed_by: string
  nb_workouts: number
  picture: string | boolean
  role: TUserRole
  suspended_at?: string | null
  suspension_report_id?: number
  username: string
}

export interface IUserProfile extends IUserLightProfile {
  bio: string | null
  birth_date: string | null
  created_reports_count?: number
  email?: string
  email_to_confirm?: string
  first_name: string | null
  last_name: string | null
  location: string | null
  nb_sports?: number
  profile_link?: string
  records: IRecord[]
  reported_count?: number
  sanctions_count?: number
  sports_list: number[]
  total_ascent: number
  total_distance: number
  total_duration: string
}

export interface IAuthUserProfile extends IUserProfile {
  analysis_visibility: TVisibilityLevels
  accepted_privacy_policy: boolean | null
  display_ascent: boolean
  email: string
  hide_profile_in_users_directory: boolean
  imperial_units: boolean
  start_elevation_at_zero: boolean
  use_raw_gpx_speed: boolean
  language: TLanguage | null
  manually_approves_followers: boolean
  map_visibility: TVisibilityLevels
  notification_preferences: TNotificationPreferences
  nb_sports: number
  records: IRecord[]
  sports_list: number[]
  timezone: string
  date_format: string
  total_distance: number
  total_duration: string
  weekm: boolean
  use_dark_mode: boolean | null
  workouts_visibility: TVisibilityLevels
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
export interface IGetUserProfilePayload {
  updateUI?: boolean
  light?: boolean
}
export interface IUserAccountUpdatePayload {
  token: LocationQueryValue | LocationQueryValue[]
  refreshUser?: boolean
}

export interface IAdminUserPayload {
  activate?: boolean
  role?: TUserRole
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
  analysis_visibility: TVisibilityLevels
  date_format: string
  display_ascent: boolean
  hide_profile_in_users_directory: boolean
  imperial_units: boolean
  language: TLanguage
  manually_approves_followers: boolean
  map_visibility: TVisibilityLevels
  start_elevation_at_zero: boolean
  timezone: string
  use_raw_gpx_speed: boolean
  weekm: boolean
  use_dark_mode: boolean | null
  workouts_visibility: TVisibilityLevels
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
  timezone?: string
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

export interface IReportActionAppeal {
  admin_user: IUserLightProfile | null
  approved: boolean | null
  created_at: string
  id: string
  reason: string | null
  text: string
  updated_at: string | null
  user: IUserLightProfile
}

export interface IUserReportAction {
  action_type: string
  appeal: IReportActionAppeal | null
  comment?: IComment | null
  created_at: string
  id: string
  reason: string
  report_id?: number
  user?: IUserProfile
  workout?: IWorkout | null
}

export interface IUserAppealPayload {
  actionId: string
  actionType: 'user_suspension' | 'user_warning'
  text: string
}

export type TToken = string | LocationQueryValue | LocationQueryValue[]

export interface IArchiveUploadTaskError {
  archive: string | null
  files: Record<string, string>
}
export type IArchiveUploadTaskStatus =
  | 'aborted'
  | 'errored'
  | 'in_progress'
  | 'queued'
  | 'successful'

export interface IArchiveUploadTask {
  created_at: string
  errored_files: IArchiveUploadTaskError
  files_count: number
  id: string
  new_workouts_count: number
  original_file_name: string | null
  progress: string
  sport_id: number | null
  status: IArchiveUploadTaskStatus
}
