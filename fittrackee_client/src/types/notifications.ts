import type { IReportForModerator } from '@/types/reports'
import type { IUserReportAction, IUserProfile } from '@/types/user'
import type { IComment, IWorkout } from '@/types/workouts'

export type TNotificationTypeWithPreferences =
  | 'account_creation'
  | 'comment_like'
  | 'follow'
  | 'follow_request'
  | 'follow_request_approved'
  | 'mention'
  | 'workout_comment'
  | 'workout_like'

export type TNotificationType =
  | TNotificationTypeWithPreferences
  | 'comment_suspension'
  | 'comment_unsuspension'
  | 'report'
  | 'suspension_appeal'
  | 'user_warning'
  | 'user_warning_appeal'
  | 'user_warning_lifting'
  | 'workout_suspension'
  | 'workout_unsuspension'

export interface INotification {
  report_action?: IUserReportAction
  comment?: IComment
  created_at: string
  id: number
  from?: IUserProfile
  marked_as_read: boolean
  report?: IReportForModerator
  type: TNotificationType
  workout?: IWorkout
}

export interface INotificationsPayload {
  page?: number
  order?: string
  status?: 'unread' | 'all'
  type?: TNotificationType
}

export interface INotificationPayload {
  notificationId: number
  markedAsRead: boolean
  currentQuery: INotificationsPayload
}

export type TNotificationPreferences = {
  [key in TNotificationTypeWithPreferences]: boolean | undefined
}
