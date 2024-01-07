import type { IUserProfile } from '@/types/user'
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

export interface IReportComment {
  created_at: string
  comment: string
  id: number
  report_id: number
  user: IUserProfile
}

export interface IReportForAdmin extends IReport {
  comments: IReportComment[]
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
