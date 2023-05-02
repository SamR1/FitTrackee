import { MutationTree } from 'vuex'

import { NOTIFICATIONS_STORE } from '@/store/constants'
import {
  INotificationsState,
  TNotificationsMutations,
} from '@/store/modules/notifications/types'
import { IPagination } from '@/types/api'
import { INotification } from '@/types/notifications'

export const mutations: MutationTree<INotificationsState> &
  TNotificationsMutations = {
  [NOTIFICATIONS_STORE.MUTATIONS.UPDATE_NOTIFICATIONS](
    state: INotificationsState,
    notifications: INotification[]
  ) {
    state.notifications = notifications
  },
  [NOTIFICATIONS_STORE.MUTATIONS.UPDATE_PAGINATION](
    state: INotificationsState,
    pagination: IPagination
  ) {
    state.pagination = pagination
  },
  [NOTIFICATIONS_STORE.MUTATIONS.UPDATE_UNREAD_STATUS](
    state: INotificationsState,
    unread: boolean
  ) {
    state.unread = unread
  },
}
