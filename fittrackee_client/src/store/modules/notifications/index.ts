import type { Module } from 'vuex'

import { actions } from '@/store/modules/notifications/actions'
import { getters } from '@/store/modules/notifications/getters'
import { mutations } from '@/store/modules/notifications/mutations'
import { notificationsState } from '@/store/modules/notifications/state'
import type { INotificationsState } from '@/store/modules/notifications/types'
import type { IRootState } from '@/store/modules/root/types'

const notifications: Module<INotificationsState, IRootState> = {
  state: notificationsState,
  actions,
  getters,
  mutations,
}

export default notifications
