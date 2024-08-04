import type { INotificationsState } from '@/store/modules/notifications/types'
import type { IPagination } from '@/types/api'

export const notificationsState: INotificationsState = {
  notifications: [],
  unread: false,
  pagination: <IPagination>{},
}
