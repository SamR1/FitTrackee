import { INotificationsState } from '@/store/modules/notifications/types'
import { IPagination } from '@/types/api'

export const notificationsState: INotificationsState = {
  notifications: [],
  unread: false,
  pagination: <IPagination>{},
}
