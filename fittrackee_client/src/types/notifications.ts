import { IReportForAdmin } from '@/types/reports'
import { IUserProfile } from '@/types/user'
import { IComment, IWorkout } from '@/types/workouts'

export type TNotificationType =
  | 'follow'
  | 'follow_request'
  | 'comment_like'
  | 'comment_reply'
  | 'mention'
  | 'report'
  | 'workout_comment'
  | 'workout_like'

export interface INotification {
  comment?: IComment
  created_at: string
  id: number
  from: IUserProfile
  marked_as_read: boolean
  report?: IReportForAdmin
  type: TNotificationType
  workout?: IWorkout
}

export interface INotificationsPayload {
  page?: number
  order?: string
  read_status?: boolean
  type?: TNotificationType
}

export interface INotificationPayload {
  notificationId: number
  markedAsRead: boolean
  currentQuery: INotificationsPayload
}
