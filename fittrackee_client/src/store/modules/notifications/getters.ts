import type { GetterTree } from 'vuex'

import { NOTIFICATIONS_STORE } from '@/store/constants'
import type {
  INotificationsGetters,
  INotificationsState,
} from '@/store/modules/notifications/types'
import type { IRootState } from '@/store/modules/root/types'

export const getters: GetterTree<INotificationsState, IRootState> &
  INotificationsGetters = {
  [NOTIFICATIONS_STORE.GETTERS.NOTIFICATIONS]: (state: INotificationsState) => {
    return state.notifications
  },
  [NOTIFICATIONS_STORE.GETTERS.PAGINATION]: (state: INotificationsState) => {
    return state.pagination
  },
  [NOTIFICATIONS_STORE.GETTERS.UNREAD_STATUS]: (state: INotificationsState) => {
    return state.unread
  },
}
