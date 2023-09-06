import { IUserProfile } from '@/types/user'
import { IComment, IWorkout } from '@/types/workouts'

export interface IReport {
  created_at: string
  note: string
  reported_by: IUserProfile
  reported_comment: IComment | null
  reported_user: IUserProfile | null
  reported_workout: IWorkout | null
  resolved: boolean
  resolved_at: string
  updated_at: string
}

export interface IFullReport extends IReport {
  reported_user: IUserProfile | null
  objectType: string
}

export interface IReportComment {
  created_at: string
  comment: string
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
  from: string
}
