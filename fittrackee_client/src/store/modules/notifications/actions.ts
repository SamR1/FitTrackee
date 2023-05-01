import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import { NOTIFICATIONS_STORE } from '@/store/constants'
import {
  INotificationsActions,
  INotificationsState,
} from '@/store/modules/notifications/types'
import { IRootState } from '@/store/modules/root/types'
import { handleError } from '@/utils'

export const actions: ActionTree<INotificationsState, IRootState> &
  INotificationsActions = {
  [NOTIFICATIONS_STORE.ACTIONS.GET_UNREAD_STATUS](
    context: ActionContext<INotificationsState, IRootState>
  ): void {
    authApi
      .get('notifications/unread')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            NOTIFICATIONS_STORE.MUTATIONS.UPDATE_UNREAD_STATUS,
            res.data.unread
          )
        }
      })
      .catch((error) => handleError(context, error))
  },
}
