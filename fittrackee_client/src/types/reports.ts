import type {
  IAdminActionAppeal,
  IUserLightProfile,
  IUserProfile,
} from '@/types/user'
import type { IComment, IWorkout } from '@/types/workouts'

export interface IReport {
  id: number
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

export interface IAdminAction {
  action_type: string
  admin_user: IUserLightProfile
  appeal: IAdminActionAppeal | null
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

export interface IReportForAdmin extends IReport {
  admin_actions?: IAdminAction[]
  comments?: IReportComment[]
}

export interface IReportPayload {
  note: string
  object_id: string
  object_type: string
  from?: string
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

export interface IReportAdminActionPayload {
  action_type: string
  reason?: string | null
  report_id: number
  username?: string
  comment_id?: string
  workout_id?: string
}
