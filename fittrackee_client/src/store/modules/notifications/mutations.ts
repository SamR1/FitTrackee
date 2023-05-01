import { MutationTree } from 'vuex'

import { NOTIFICATIONS_STORE } from '@/store/constants'
import {
  INotificationsState,
  TNotificationsMutations,
} from '@/store/modules/notifications/types'

export const mutations: MutationTree<INotificationsState> &
  TNotificationsMutations = {
  [NOTIFICATIONS_STORE.MUTATIONS.UPDATE_UNREAD_STATUS](
    state: INotificationsState,
    unread: boolean
  ) {
    state.unread = unread
  },
}
