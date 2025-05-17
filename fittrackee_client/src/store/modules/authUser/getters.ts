import type { GetterTree } from 'vuex'

import { AUTH_USER_STORE } from '@/store/constants'
import type {
  IAuthUserGetters,
  IAuthUserState,
} from '@/store/modules/authUser/types'
import type { IRootState } from '@/store/modules/root/types'

export const getters: GetterTree<IAuthUserState, IRootState> &
  IAuthUserGetters = {
  [AUTH_USER_STORE.GETTERS.AUTH_TOKEN]: (state: IAuthUserState) => {
    return state.authToken
  },
  [AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]: (state: IAuthUserState) => {
    return state.authUserProfile
  },
  [AUTH_USER_STORE.GETTERS.BLOCKED_USERS]: (state: IAuthUserState) => {
    return state.blockedUsers
  },
  [AUTH_USER_STORE.GETTERS.FOLLOW_REQUESTS]: (state: IAuthUserState) => {
    return state.followRequests
  },
  [AUTH_USER_STORE.GETTERS.EXPORT_REQUEST]: (state: IAuthUserState) => {
    return state.exportRequest
  },
  [AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED]: (state: IAuthUserState) => {
    return state.authToken !== null
  },
  [AUTH_USER_STORE.GETTERS.HAS_ADMIN_RIGHTS]: (state: IAuthUserState) => {
    return (
      state.authUserProfile &&
      ['admin', 'owner'].includes(state.authUserProfile.role)
    )
  },
  [AUTH_USER_STORE.GETTERS.HAS_MODERATOR_RIGHTS]: (state: IAuthUserState) => {
    return (
      state.authUserProfile &&
      ['admin', 'moderator', 'owner'].includes(state.authUserProfile.role)
    )
  },
  [AUTH_USER_STORE.GETTERS.HAS_OWNER_RIGHTS]: (state: IAuthUserState) => {
    return state.authUserProfile && state.authUserProfile.role === 'owner'
  },
  [AUTH_USER_STORE.GETTERS.IS_REGISTRATION_SUCCESS]: (
    state: IAuthUserState
  ) => {
    return state.isRegistrationSuccess
  },
  [AUTH_USER_STORE.GETTERS.IS_SUCCESS]: (state: IAuthUserState) => {
    return state.isSuccess
  },
  [AUTH_USER_STORE.GETTERS.IS_SUSPENDED]: (state: IAuthUserState) => {
    return state.authUserProfile && state.authUserProfile.suspended_at !== null
  },
  [AUTH_USER_STORE.GETTERS.IS_PROFILE_LOADED]: (state: IAuthUserState) => {
    return state.authUserProfile?.username !== undefined
  },
  [AUTH_USER_STORE.GETTERS.USER_LOADING]: (state: IAuthUserState) => {
    return state.loading
  },
  [AUTH_USER_STORE.GETTERS.IS_PROFILE_NOT_LOADED]: (state: IAuthUserState) => {
    return state.authUserProfile.username === undefined
  },
  [AUTH_USER_STORE.GETTERS.ACCOUNT_SUSPENSION]: (state: IAuthUserState) => {
    return state.userReportAction
  },
  [AUTH_USER_STORE.GETTERS.USER_SANCTION]: (state: IAuthUserState) => {
    return state.userReportAction
  },
  [AUTH_USER_STORE.GETTERS.TIMEZONES]: (state: IAuthUserState) => {
    return state.timezones
  },
  [AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASK]: (state: IAuthUserState) => {
    return state.archiveUploadTasks.task
  },
  [AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASKS]: (state: IAuthUserState) => {
    return state.archiveUploadTasks.tasks
  },
  [AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASKS_LOADING]: (
    state: IAuthUserState
  ) => {
    return state.archiveUploadTasks.loading
  },
  [AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASKS_PAGINATION]: (
    state: IAuthUserState
  ) => {
    return state.archiveUploadTasks.pagination
  },
}
