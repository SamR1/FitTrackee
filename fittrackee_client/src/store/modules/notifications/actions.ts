import type { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import { NOTIFICATIONS_STORE, ROOT_STORE } from '@/store/constants'
import type {
  INotificationsActions,
  INotificationsState,
} from '@/store/modules/notifications/types'
import type { IRootState } from '@/store/modules/root/types'
import type {
  INotificationPayload,
  INotificationsPayload,
} from '@/types/notifications'
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
  [NOTIFICATIONS_STORE.ACTIONS.GET_NOTIFICATION_TYPES](
    context: ActionContext<INotificationsState, IRootState>,
    payload: INotificationsPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('notifications/types', { params: payload })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            NOTIFICATIONS_STORE.MUTATIONS.UPDATE_TYPES,
            res.data.notification_types
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        if (error.message !== 'canceled') {
          handleError(context, error)
        }
      })
  },
  [NOTIFICATIONS_STORE.ACTIONS.GET_NOTIFICATIONS](
    context: ActionContext<INotificationsState, IRootState>,
    payload: INotificationsPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('notifications', { params: payload })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            NOTIFICATIONS_STORE.MUTATIONS.UPDATE_NOTIFICATIONS,
            res.data.notifications
          )
          context.commit(
            NOTIFICATIONS_STORE.MUTATIONS.UPDATE_PAGINATION,
            res.data.pagination
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        if (error.message !== 'canceled') {
          handleError(context, error)
        }
      })
  },
  [NOTIFICATIONS_STORE.ACTIONS.MARK_ALL_AS_READ](
    context: ActionContext<INotificationsState, IRootState>,
    payload: INotificationsPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    const data: Record<string, string> = {}
    if (payload.type) {
      data['type'] = payload.type
    }
    authApi
      .post('notifications/mark-all-as-read', data)
      .then((res) => {
        if (res.data.status === 'success') {
          context.dispatch(
            NOTIFICATIONS_STORE.ACTIONS.GET_NOTIFICATIONS,
            payload
          )
          context.dispatch(NOTIFICATIONS_STORE.ACTIONS.GET_UNREAD_STATUS)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        if (error.message !== 'canceled') {
          handleError(context, error)
        }
      })
  },
  [NOTIFICATIONS_STORE.ACTIONS.UPDATE_STATUS](
    context: ActionContext<INotificationsState, IRootState>,
    payload: INotificationPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .patch(`notifications/${payload.notificationId}`, {
        read_status: payload.markedAsRead,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context.dispatch(
            NOTIFICATIONS_STORE.ACTIONS.GET_NOTIFICATIONS,
            payload.currentQuery
          )
          context.dispatch(NOTIFICATIONS_STORE.ACTIONS.GET_UNREAD_STATUS)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        if (error.message !== 'canceled') {
          handleError(context, error)
        }
      })
  },
}
