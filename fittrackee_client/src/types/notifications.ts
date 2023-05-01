import { IUserProfile } from '@/types/user'
import { IComment, IWorkout } from '@/types/workouts'

export type TNotificationType =
  | 'follow'
  | 'follow_request'
  | 'comment_like'
  | 'comment_reply'
  | 'mention'
  | 'workout_comment'
  | 'workout_like'

export interface INotification {
  comment?: IComment
  created_at: string
  from: IUserProfile
  marked_as_read: boolean
  reply?: IComment
  type: TNotificationType
  workout?: IWorkout
}

export interface INotificationPayload {
  page?: number
  order?: string
  read_status: boolean
  type?: TNotificationType
}
