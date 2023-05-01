import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { NOTIFICATIONS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IPagination } from '@/types/api'
import { INotification } from '@/types/notifications'

export interface INotificationsState {
  notifications: INotification[]
  unread: boolean
  pagination: IPagination
}

export interface INotificationsActions {
  [NOTIFICATIONS_STORE.ACTIONS.GET_UNREAD_STATUS](
    context: ActionContext<INotificationsState, IRootState>
  ): void
}

export interface INotificationsGetters {
  [NOTIFICATIONS_STORE.GETTERS.UNREAD_STATUS](
    state: INotificationsState
  ): boolean
}

export type TNotificationsMutations<S = INotificationsState> = {
  [NOTIFICATIONS_STORE.MUTATIONS.UPDATE_UNREAD_STATUS](
    state: S,
    unread: boolean
  ): void
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
    P extends Parameters<TNotificationsMutations[K]>[1]
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TNotificationsMutations[K]>
}
