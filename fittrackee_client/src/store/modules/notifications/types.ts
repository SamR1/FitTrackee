import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { NOTIFICATIONS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { IPagination } from '@/types/api'
import type {
  INotification,
  INotificationPayload,
  INotificationsPayload,
} from '@/types/notifications'

export interface INotificationsState {
  notifications: INotification[]
  unread: boolean
  pagination: IPagination
}

export interface INotificationsActions {
  [NOTIFICATIONS_STORE.ACTIONS.GET_NOTIFICATIONS](
    context: ActionContext<INotificationsState, IRootState>,
    payload: INotificationsPayload
  ): void
  [NOTIFICATIONS_STORE.ACTIONS.GET_UNREAD_STATUS](
    context: ActionContext<INotificationsState, IRootState>
  ): void
  [NOTIFICATIONS_STORE.ACTIONS.MARK_ALL_AS_READ](
    context: ActionContext<INotificationsState, IRootState>,
    payload: INotificationsPayload
  ): void
  [NOTIFICATIONS_STORE.ACTIONS.UPDATE_STATUS](
    context: ActionContext<INotificationsState, IRootState>,
    payload: INotificationPayload
  ): void
}

export interface INotificationsGetters {
  [NOTIFICATIONS_STORE.GETTERS.NOTIFICATIONS](
    state: INotificationsState
  ): INotification[]
  [NOTIFICATIONS_STORE.GETTERS.PAGINATION](
    state: INotificationsState
  ): IPagination
  [NOTIFICATIONS_STORE.GETTERS.UNREAD_STATUS](
    state: INotificationsState
  ): boolean
}

export type TNotificationsMutations<S = INotificationsState> = {
  [NOTIFICATIONS_STORE.MUTATIONS.UPDATE_NOTIFICATIONS](
    state: S,
    notifications: INotification[]
  ): void
  [NOTIFICATIONS_STORE.MUTATIONS.UPDATE_PAGINATION](
    state: S,
    pagination: IPagination
  ): void
  [NOTIFICATIONS_STORE.MUTATIONS.UPDATE_UNREAD_STATUS](
    state: S,
    unread: boolean
  ): void
  [NOTIFICATIONS_STORE.MUTATIONS.EMPTY_NOTIFICATIONS](state: S): void
}

export type TNotificationsStoreModule<S = INotificationsState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof INotificationsActions>(
    key: K,
    payload?: Parameters<INotificationsActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<INotificationsActions[K]>
} & {
  getters: {
    [K in keyof INotificationsGetters]: ReturnType<INotificationsGetters[K]>
  }
} & {
  commit<
    K extends keyof TNotificationsMutations,
    P extends Parameters<TNotificationsMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TNotificationsMutations[K]>
}
