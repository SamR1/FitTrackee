import type { MutationTree } from 'vuex'

import { NOTIFICATIONS_STORE } from '@/store/constants'
import type {
  INotificationsState,
  TNotificationsMutations,
} from '@/store/modules/notifications/types'
import type { IPagination } from '@/types/api'
import type { INotification, TNotificationType } from '@/types/notifications'

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
  [NOTIFICATIONS_STORE.MUTATIONS.UPDATE_TYPES](
    state: INotificationsState,
    types: TNotificationType[]
  ) {
    state.types = types
  },
  [NOTIFICATIONS_STORE.MUTATIONS.UPDATE_UNREAD_STATUS](
    state: INotificationsState,
    unread: boolean
  ) {
    state.unread = unread
  },
  [NOTIFICATIONS_STORE.MUTATIONS.EMPTY_NOTIFICATIONS](
    state: INotificationsState
  ) {
    state.notifications = []
    state.pagination = <IPagination>{}
  },
}
