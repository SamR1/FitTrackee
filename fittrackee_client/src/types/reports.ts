import type {
  IReportActionAppeal,
  IUserLightProfile,
  IUserProfile,
} from '@/types/user'
import type { IComment, IWorkout } from '@/types/workouts'

export interface IReport {
  id: number
  is_reported_user_warned: boolean
  created_at: string
  note: string
  object_type: string
  reported_by: IUserProfile | null
  reported_comment: IComment | null
  reported_user: IUserProfile | null
  reported_workout: IWorkout | null
  resolved: boolean
  resolved_at: string
  resolved_by: null | IUserProfile
  updated_at: string
}

export interface IReportAction {
  action_type: string
  moderator: IUserLightProfile
  appeal: IReportActionAppeal | null
  created_at: string
  id: number
  reason: string | null
  report_id: number | null
  user: IUserLightProfile | null
}

export interface IReportComment {
  created_at: string
  comment: string
  id: number
  report_id: number
  user: IUserProfile
}

export interface IReportForModerator extends IReport {
  report_actions?: IReportAction[]
  comments?: IReportComment[]
}

export interface IReportPayload {
  note: string
  object_id: string
  object_type: string
  from?: string
}

export interface IGetReportPayload {
  reportId: number
  loader: 'REPORT' | 'REPORT_UPDATE'
}

export interface IReportCommentPayload {
  reportId: number
  comment: string
  resolved?: boolean
}

export type TReportAction =
  | 'ADD_COMMENT'
  | 'MARK_AS_RESOLVED'
  | 'MARK_AS_UNRESOLVED'
  | 'SEND_WARNING_EMAIL'
  | 'SUSPEND_ACCOUNT'
  | 'SUSPEND_CONTENT'
  | 'UNSUSPEND_ACCOUNT'
  | 'UNSUSPEND_CONTENT'

export interface IAppealPayload {
  appealId: string
  approved: boolean
  reason: string
  reportId: number
}

export interface IReportActionPayload {
  action_type: string
  reason?: string | null
  report_id: number
  username?: string
  comment_id?: string
  workout_id?: string
}
