import type { MutationTree } from 'vuex'

import { USERS_STORE } from '@/store/constants'
import type { IUsersState, TUsersMutations } from '@/store/modules/users/types'
import type { IPagination } from '@/types/api'
import type { IQueuedTask, TQueuedTasksCounts } from '@/types/application.ts'
import type { IReportAction } from '@/types/reports'
import type { IUserProfile } from '@/types/user'
import type { IWorkout } from '@/types/workouts.ts'

export const mutations: MutationTree<IUsersState> & TUsersMutations = {
  [USERS_STORE.MUTATIONS.UPDATE_USER](state: IUsersState, user: IUserProfile) {
    state.user = user
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_IN_USERS](
    state: IUsersState,
    updatedUser: IUserProfile
  ) {
    state.users = state.users.map((user) => {
      if (user.username === updatedUser.username) {
        return updatedUser
      }
      return user
    })
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_IN_RELATIONSHIPS](
    state: IUsersState,
    updatedUser: IUserProfile
  ) {
    state.user_relationships = state.user_relationships.map((user) => {
      if (user.username === updatedUser.username) {
        return updatedUser
      }
      return user
    })
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_RELATIONSHIPS](
    state: IUsersState,
    relationships: IUserProfile[]
  ) {
    state.user_relationships = relationships
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS](
    state: IUsersState,
    sanctions: IReportAction[]
  ) {
    state.userSanctions.sanctions = sanctions
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS_LOADING](
    state: IUsersState,
    loading: boolean
  ) {
    state.userSanctions.loading = loading
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS_PAGINATION](
    state: IUsersState,
    pagination: IPagination
  ) {
    state.userSanctions.pagination = pagination
  },
  [USERS_STORE.MUTATIONS.UPDATE_USERS](
    state: IUsersState,
    users: IUserProfile[]
  ) {
    state.users = users
  },
  [USERS_STORE.MUTATIONS.UPDATE_USERS_LOADING](
    state: IUsersState,
    loading: boolean
  ) {
    state.loading = loading
  },
  [USERS_STORE.MUTATIONS.UPDATE_USERS_PAGINATION](
    state: IUsersState,
    pagination: IPagination
  ) {
    state.pagination = pagination
  },
  [USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS](
    state: IUsersState,
    isSuccess: boolean
  ) {
    state.isSuccess = isSuccess
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_CURRENT_REPORTING](
    state: IUsersState,
    currentReporting: boolean
  ) {
    state.currentReporting = currentReporting
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_WORKOUTS](
    state: IUsersState,
    userWorkouts: IWorkout[]
  ) {
    state.userWorkouts.workouts = userWorkouts
  },
  [USERS_STORE.MUTATIONS.UPDATE_USER_WORKOUTS_LOADING](
    state: IUsersState,
    loading: boolean
  ) {
    state.userWorkouts.loading = loading
  },
  [USERS_STORE.MUTATIONS.UPDATE_USERS_QUEUED_TASKS](
    state: IUsersState,
    tasks: IQueuedTask[]
  ) {
    state.usersQueuedTasks.tasks = tasks
  },
  [USERS_STORE.MUTATIONS.UPDATE_USERS_QUEUED_TASKS_COUNTS](
    state: IUsersState,
    counts: TQueuedTasksCounts
  ) {
    state.usersQueuedTasks.counts = counts
  },
  [USERS_STORE.MUTATIONS.UPDATE_USERS_QUEUED_TASKS_PAGINATION](
    state: IUsersState,
    pagination: IPagination
  ) {
    state.usersQueuedTasks.pagination = pagination
  },
}
