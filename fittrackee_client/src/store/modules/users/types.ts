import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { USERS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { IPagination } from '@/types/api'
import type {
  IQueuedTask,
  IQueuedTasksPayload,
  TQueuedTasksCounts,
} from '@/types/application.ts'
import type { IReportAction } from '@/types/reports'
import type {
  IAdminUserPayload,
  IUserDeletionPayload,
  IUserProfile,
  IUserRelationshipActionPayload,
  IUserRelationshipsPayload,
  TUsersPayload,
} from '@/types/user'
import type { IWorkout } from '@/types/workouts.ts'

export interface IUsersState {
  user: IUserProfile
  userSanctions: {
    sanctions: IReportAction[]
    loading: boolean
    pagination: IPagination
  }
  userWorkouts: {
    workouts: IWorkout[]
    loading: boolean
  }
  user_relationships: IUserProfile[]
  users: IUserProfile[]
  loading: boolean
  isSuccess: boolean
  pagination: IPagination
  currentReporting: boolean
  usersQueuedTasks: {
    counts: TQueuedTasksCounts
    tasks: IQueuedTask[]
    pagination: IPagination
  }
}

export interface IUsersActions {
  [USERS_STORE.ACTIONS.EMPTY_USER](
    context: ActionContext<IUsersState, IRootState>
  ): void
  [USERS_STORE.ACTIONS.EMPTY_USERS](
    context: ActionContext<IUsersState, IRootState>
  ): void
  [USERS_STORE.ACTIONS.EMPTY_RELATIONSHIPS](
    context: ActionContext<IUsersState, IRootState>
  ): void
  [USERS_STORE.ACTIONS.GET_USER](
    context: ActionContext<IUsersState, IRootState>,
    username: string
  ): void
  [USERS_STORE.ACTIONS.GET_USER_SANCTIONS](
    context: ActionContext<IUsersState, IRootState>,
    payload: TUsersPayload
  ): void
  [USERS_STORE.ACTIONS.GET_USER_WORKOUTS](
    context: ActionContext<IUsersState, IRootState>,
    username: string
  ): void
  [USERS_STORE.ACTIONS.GET_USERS](
    context: ActionContext<IUsersState, IRootState>,
    payload: TUsersPayload
  ): void
  [USERS_STORE.ACTIONS.GET_USERS_FOR_ADMIN](
    context: ActionContext<IUsersState, IRootState>,
    payload: TUsersPayload
  ): void
  [USERS_STORE.ACTIONS.UPDATE_USER](
    context: ActionContext<IUsersState, IRootState>,
    payload: IAdminUserPayload
  ): void
  [USERS_STORE.ACTIONS.UPDATE_RELATIONSHIP](
    context: ActionContext<IUsersState, IRootState>,
    payload: IUserRelationshipActionPayload
  ): void
  [USERS_STORE.ACTIONS.GET_RELATIONSHIPS](
    context: ActionContext<IUsersState, IRootState>,
    payload: IUserRelationshipsPayload
  ): void
  [USERS_STORE.ACTIONS.DELETE_USER_ACCOUNT](
    context: ActionContext<IUsersState, IRootState>,
    payload: IUserDeletionPayload
  ): void
  [USERS_STORE.ACTIONS.GET_USERS_QUEUED_TASKS_LIST](
    context: ActionContext<IUsersState, IRootState>,
    payload: IQueuedTasksPayload
  ): void
  [USERS_STORE.ACTIONS.GET_USERS_QUEUED_TASKS_COUNT](
    context: ActionContext<IUsersState, IRootState>
  ): void
}

export interface IUsersGetters {
  [USERS_STORE.GETTERS.USER](state: IUsersState): IUserProfile
  [USERS_STORE.GETTERS.USER_CURRENT_REPORTING](state: IUsersState): boolean
  [USERS_STORE.GETTERS.USER_RELATIONSHIPS](state: IUsersState): IUserProfile[]
  [USERS_STORE.GETTERS.USER_SANCTIONS](state: IUsersState): IReportAction[]
  [USERS_STORE.GETTERS.USER_SANCTIONS_LOADING](state: IUsersState): boolean
  [USERS_STORE.GETTERS.USER_SANCTIONS_PAGINATION](
    state: IUsersState
  ): IPagination
  [USERS_STORE.GETTERS.USER_WORKOUTS](state: IUsersState): IWorkout[]
  [USERS_STORE.GETTERS.USER_WORKOUTS_LOADING](state: IUsersState): boolean
  [USERS_STORE.GETTERS.USERS](state: IUsersState): IUserProfile[]
  [USERS_STORE.GETTERS.USERS_IS_SUCCESS](state: IUsersState): boolean
  [USERS_STORE.GETTERS.USERS_LOADING](state: IUsersState): boolean
  [USERS_STORE.GETTERS.USERS_PAGINATION](state: IUsersState): IPagination
  [USERS_STORE.GETTERS.USERS_QUEUED_TASKS](state: IUsersState): IQueuedTask[]
  [USERS_STORE.GETTERS.USERS_QUEUED_TASKS_COUNTS](
    state: IUsersState
  ): TQueuedTasksCounts
  [USERS_STORE.GETTERS.USERS_QUEUED_TASKS_PAGINATION](
    state: IUsersState
  ): IPagination
}

export type TUsersMutations<S = IUsersState> = {
  [USERS_STORE.MUTATIONS.UPDATE_USER](state: S, user: IUserProfile): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS](
    state: S,
    updatedUser: IUserProfile
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_IN_RELATIONSHIPS](
    state: S,
    updatedUser: IUserProfile
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_RELATIONSHIPS](
    state: S,
    relationship: IUserProfile[]
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS](
    state: S,
    sanctions: IReportAction[]
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS_LOADING](
    state: S,
    loading: boolean
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS_PAGINATION](
    state: S,
    pagination: IPagination
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS](state: S, users: IUserProfile[]): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING](state: S, loading: boolean): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS_PAGINATION](
    state: S,
    pagination: IPagination
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS](state: S, isSuccess: boolean): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_CURRENT_REPORTING](
    state: S,
    currentReporting: boolean
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_WORKOUTS](
    state: S,
    userWorkouts: IWorkout[]
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USER_WORKOUTS_LOADING](
    state: S,
    loading: boolean
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS_QUEUED_TASKS](
    state: S,
    tasks: IQueuedTask[]
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS_QUEUED_TASKS_COUNTS](
    state: S,
    counts: TQueuedTasksCounts
  ): void
  [USERS_STORE.MUTATIONS.UPDATE_USERS_QUEUED_TASKS_PAGINATION](
    state: S,
    pagination: IPagination
  ): void
}

export type TUsersStoreModule<S = IUsersState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IUsersActions>(
    key: K,
    payload?: Parameters<IUsersActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IUsersActions[K]>
} & {
  getters: {
    [K in keyof IUsersGetters]: ReturnType<IUsersGetters[K]>
  }
} & {
  commit<
    K extends keyof TUsersMutations,
    P extends Parameters<TUsersMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TUsersMutations[K]>
}
