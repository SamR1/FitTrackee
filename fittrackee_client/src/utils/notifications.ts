import type { TNotificationTypeWithPreferences } from '@/types/notifications.ts'
import type { TUserRole } from '@/types/user.ts'

export const getNotificationTypes = (role: TUserRole) => {
  const types: TNotificationTypeWithPreferences[] = [
    'follow',
    'follow_request',
    'follow_request_approved',
    'workout_like',
    'workout_comment',
    'comment_reply',
    'comment_like',
    'mention',
  ]
  if (role === 'admin' || role === 'owner') {
    types.push('account_creation')
  }
  return types
}
