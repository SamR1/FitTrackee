import type { IAccountSuspensionAppeal, IUserProfile } from '@/types/user'
import type { IComment, IWorkout } from '@/types/workouts'

export interface IReport {
  id: number
  created_at: string
  note: string
  object_type: string
  reported_by: IUserProfile
  reported_comment: IComment | null
  reported_user: IUserProfile
  reported_workout: IWorkout | null
  resolved: boolean
  resolved_at: string
  resolved_by: null | IUserProfile
  updated_at: string
}

export interface IAdminAction {
  action_type: string
  admin_user: IUserProfile
  appeal: IAccountSuspensionAppeal | null
  created_at: string
  id: number
  reason: string | null
  report_id: number | null
  user: IUserProfile | null
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
  | 'SUSPEND_ACCOUNT'
  | 'UNSUSPEND_ACCOUNT'

export interface IAppealPayload {
  appealId: string
  approved: boolean
  reason: string
  reportId: number
}
